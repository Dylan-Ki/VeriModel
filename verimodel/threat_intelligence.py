"""
Threat Intelligence Module

Tích hợp với VirusTotal API để tra cứu hash/IP/domain đáng ngờ.
"""

import hashlib
import re
import os
from pathlib import Path
from typing import Dict, List, Optional, Set
import time

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class ThreatIntelligence:
    """
    Tra cứu Threat Intelligence từ VirusTotal và các nguồn khác.
    """

    # Regex patterns để phát hiện IOCs
    IP_PATTERN = re.compile(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b')
    DOMAIN_PATTERN = re.compile(r'\b([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b')
    MD5_PATTERN = re.compile(r'\b[0-9a-fA-F]{32}\b')
    SHA1_PATTERN = re.compile(r'\b[0-9a-fA-F]{40}\b')
    SHA256_PATTERN = re.compile(r'\b[0-9a-fA-F]{64}\b')

    def __init__(self, virustotal_api_key: Optional[str] = None):
        """
        Khởi tạo Threat Intelligence.
        
        Args:
            virustotal_api_key: API key của VirusTotal (có thể lấy từ env VIRUSTOTAL_API_KEY)
        """
        self.vt_api_key = virustotal_api_key or os.getenv("VIRUSTOTAL_API_KEY")
        self.vt_base_url = "https://www.virustotal.com/vtapi/v2"
        self.rate_limit_delay = 16  # VirusTotal giới hạn 4 requests/phút (15s/request)

    def extract_iocs_from_content(self, content: bytes, file_path: Optional[Path] = None) -> Dict[str, Set[str]]:
        """
        Trích xuất IOCs (Indicators of Compromise) từ nội dung file.
        
        Args:
            content: Nội dung file dạng bytes
            file_path: Đường dẫn file (để tính hash)
            
        Returns:
            Dict chứa các IOCs đã phát hiện: {"hashes": {...}, "ips": {...}, "domains": {...}}
        """
        iocs = {
            "hashes": set(),
            "ips": set(),
            "domains": set(),
        }

        # Tính hash của file
        if file_path and file_path.exists():
            try:
                md5_hash = hashlib.md5(content).hexdigest()
                sha1_hash = hashlib.sha1(content).hexdigest()
                sha256_hash = hashlib.sha256(content).hexdigest()
                iocs["hashes"].update([md5_hash, sha1_hash, sha256_hash])
            except Exception:
                pass

        # Chuyển sang string để tìm IOCs (chỉ tìm trong printable strings)
        try:
            content_str = content.decode('utf-8', errors='ignore')
        except Exception:
            content_str = ""
        
        # Tìm IP addresses
        ips = self.IP_PATTERN.findall(content_str)
        # Loại bỏ local/private IPs (tùy chọn, có thể giữ lại để báo cáo)
        for ip in ips:
            if not self._is_private_ip(ip):
                iocs["ips"].add(ip)

        # Tìm domains
        domains = self.DOMAIN_PATTERN.findall(content_str)
        for domain_tuple in domains:
            domain = domain_tuple[0] if isinstance(domain_tuple, tuple) else domain_tuple
            # Loại bỏ các domain phổ biến/không đáng ngờ
            if not self._is_benign_domain(domain):
                iocs["domains"].add(domain)

        # Tìm hash strings trong content
        md5_hashes = self.MD5_PATTERN.findall(content_str)
        sha1_hashes = self.SHA1_PATTERN.findall(content_str)
        sha256_hashes = self.SHA256_PATTERN.findall(content_str)
        iocs["hashes"].update(md5_hashes + sha1_hashes + sha256_hashes)

        # Chuyển set thành list để JSON serializable
        return {
            "hashes": list(iocs["hashes"]),
            "ips": list(iocs["ips"]),
            "domains": list(iocs["domains"]),
        }

    def _is_private_ip(self, ip: str) -> bool:
        """Kiểm tra xem IP có phải là private/local không."""
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        first_octet = int(parts[0])
        return (first_octet == 10 or 
                (first_octet == 172 and 16 <= int(parts[1]) <= 31) or
                (first_octet == 192 and int(parts[1]) == 168) or
                first_octet == 127)

    def _is_benign_domain(self, domain: str) -> bool:
        """Kiểm tra xem domain có phải là domain phổ biến/không đáng ngờ không."""
        benign_domains = [
            'localhost', 'example.com', 'test.com', 'github.com',
            'python.org', 'pypi.org', 'pytorch.org', 'tensorflow.org'
        ]
        domain_lower = domain.lower()
        return any(bd in domain_lower for bd in benign_domains)

    def query_virustotal_hash(self, file_hash: str) -> Optional[Dict]:
        """
        Tra cứu hash trên VirusTotal.
        
        Args:
            file_hash: MD5, SHA1, hoặc SHA256 hash
            
        Returns:
            Dict chứa kết quả từ VirusTotal hoặc None nếu lỗi
        """
        if not self.vt_api_key or not REQUESTS_AVAILABLE:
            return None

        try:
            url = f"{self.vt_base_url}/file/report"
            params = {
                "apikey": self.vt_api_key,
                "resource": file_hash
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("response_code") == 1:  # Found
                    return {
                        "found": True,
                        "permalink": data.get("permalink"),
                        "positives": data.get("positives", 0),
                        "total": data.get("total", 0),
                        "scan_date": data.get("scan_date"),
                        "scans": data.get("scans", {}),
                    }
                elif data.get("response_code") == 0:
                    return {"found": False, "message": "Hash not found in VirusTotal database"}
            elif response.status_code == 204:
                return {"error": "Rate limit exceeded"}
            else:
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}

    def query_virustotal_ip(self, ip: str) -> Optional[Dict]:
        """
        Tra cứu IP address trên VirusTotal.
        
        Args:
            ip: IP address
            
        Returns:
            Dict chứa kết quả từ VirusTotal hoặc None nếu lỗi
        """
        if not self.vt_api_key or not REQUESTS_AVAILABLE:
            return None

        try:
            url = f"{self.vt_base_url}/ip-address/report"
            params = {
                "apikey": self.vt_api_key,
                "ip": ip
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("response_code") == 1:
                    return {
                        "found": True,
                        "asn": data.get("asn"),
                        "country": data.get("country"),
                        "detected_urls": data.get("detected_urls", []),
                        "undetected_urls": data.get("undetected_urls", []),
                    }
                else:
                    return {"found": False}
            elif response.status_code == 204:
                return {"error": "Rate limit exceeded"}
            else:
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}

    def query_virustotal_domain(self, domain: str) -> Optional[Dict]:
        """
        Tra cứu domain trên VirusTotal.
        
        Args:
            domain: Domain name
            
        Returns:
            Dict chứa kết quả từ VirusTotal hoặc None nếu lỗi
        """
        if not self.vt_api_key or not REQUESTS_AVAILABLE:
            return None

        try:
            url = f"{self.vt_base_url}/domain/report"
            params = {
                "apikey": self.vt_api_key,
                "domain": domain
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("response_code") == 1:
                    return {
                        "found": True,
                        "categories": data.get("categories", {}),
                        "detected_urls": data.get("detected_urls", []),
                        "undetected_urls": data.get("undetected_urls", []),
                        "subdomains": data.get("subdomains", []),
                    }
                else:
                    return {"found": False}
            elif response.status_code == 204:
                return {"error": "Rate limit exceeded"}
            else:
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}

    def analyze_file(self, file_path: Path, check_vt: bool = True) -> Dict:
        """
        Phân tích file và tra cứu Threat Intelligence.
        
        Args:
            file_path: Đường dẫn file cần phân tích
            check_vt: Có tra cứu VirusTotal hay không
            
        Returns:
            Dict chứa kết quả phân tích và threat intelligence
        """
        if not file_path.exists():
            return {"error": f"File không tồn tại: {file_path}"}

        result = {
            "iocs": {},
            "virustotal_results": {},
            "threats": [],
            "warnings": [],
        }

        try:
            content = file_path.read_bytes()
            
            # Trích xuất IOCs
            iocs = self.extract_iocs_from_content(content, file_path)
            result["iocs"] = iocs

            # Tra cứu VirusTotal nếu có API key
            if check_vt and self.vt_api_key:
                vt_results = {}
                
                # Tra cứu hash của file (chỉ SHA256 để tránh rate limit)
                if iocs["hashes"]:
                    sha256_hashes = [h for h in iocs["hashes"] if len(h) == 64]
                    if sha256_hashes:
                        sha256 = sha256_hashes[0]  # Lấy hash đầu tiên (file hash)
                        vt_hash_result = self.query_virustotal_hash(sha256)
                        if vt_hash_result:
                            vt_results["file_hash"] = vt_hash_result
                            if vt_hash_result.get("found") and vt_hash_result.get("positives", 0) > 0:
                                result["threats"].append({
                                    "type": "VIRUSTOTAL_HASH",
                                    "severity": "HIGH",
                                    "description": f"File hash được phát hiện bởi {vt_hash_result['positives']}/{vt_hash_result['total']} antivirus engines trên VirusTotal",
                                    "virustotal_permalink": vt_hash_result.get("permalink"),
                                })
                        time.sleep(self.rate_limit_delay)  # Rate limiting

                # Tra cứu IPs
                for ip in iocs["ips"][:3]:  # Giới hạn 3 IPs để tránh rate limit
                    vt_ip_result = self.query_virustotal_ip(ip)
                    if vt_ip_result:
                        vt_results[f"ip_{ip}"] = vt_ip_result
                        if vt_ip_result.get("found") and vt_ip_result.get("detected_urls"):
                            result["warnings"].append({
                                "type": "SUSPICIOUS_IP",
                                "severity": "MEDIUM",
                                "description": f"IP {ip} có liên quan đến các URL độc hại trên VirusTotal",
                                "ip": ip,
                            })
                    time.sleep(self.rate_limit_delay)

                # Tra cứu domains
                for domain in iocs["domains"][:3]:  # Giới hạn 3 domains
                    vt_domain_result = self.query_virustotal_domain(domain)
                    if vt_domain_result:
                        vt_results[f"domain_{domain}"] = vt_domain_result
                        if vt_domain_result.get("found") and vt_domain_result.get("detected_urls"):
                            result["warnings"].append({
                                "type": "SUSPICIOUS_DOMAIN",
                                "severity": "MEDIUM",
                                "description": f"Domain {domain} có liên quan đến các URL độc hại trên VirusTotal",
                                "domain": domain,
                            })
                    time.sleep(self.rate_limit_delay)

                result["virustotal_results"] = vt_results

            # Cảnh báo nếu có IOCs nhưng không có API key
            if not self.vt_api_key and (iocs["ips"] or iocs["domains"]):
                result["warnings"].append({
                    "type": "TI_UNAVAILABLE",
                    "severity": "LOW",
                    "description": "Phát hiện IOCs nhưng không có VirusTotal API key để tra cứu. Đặt VIRUSTOTAL_API_KEY environment variable.",
                    "iocs_found": len(iocs["ips"]) + len(iocs["domains"]),
                })

        except Exception as e:
            result["error"] = f"Lỗi khi phân tích file: {str(e)}"

        return result

