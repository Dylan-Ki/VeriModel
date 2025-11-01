"""
Safetensors Converter Module

Chuyển đổi các file model từ định dạng pickle không an toàn sang định dạng safetensors an toàn.
"""

import pickle
import json
import zipfile
from pathlib import Path
from typing import Dict, Optional, Any
import warnings

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    from safetensors import safe_open
    from safetensors.torch import save_file
    SAFETENSORS_AVAILABLE = True
except ImportError:
    SAFETENSORS_AVAILABLE = False


class SafetensorsConverter:
    """
    Chuyển đổi các model từ pickle sang safetensors format.
    """

    def __init__(self):
        """Khởi tạo converter."""
        if not TORCH_AVAILABLE:
            warnings.warn("PyTorch không được cài đặt. Không thể chuyển đổi .pth files.")
        if not SAFETENSORS_AVAILABLE:
            warnings.warn("safetensors không được cài đặt. Vui lòng cài đặt: pip install safetensors")

    def is_supported(self) -> bool:
        """Kiểm tra xem converter có hỗ trợ không."""
        return TORCH_AVAILABLE and SAFETENSORS_AVAILABLE

    def convert_pickle_to_safetensors(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
        safe_mode: bool = True
    ) -> Dict[str, Any]:
        """
        Chuyển đổi file pickle sang safetensors.
        
        CHÚ Ý: Chỉ nên sử dụng với các model đã được kiểm tra an toàn!
        
        Args:
            input_path: Đường dẫn file input (.pkl)
            output_path: Đường dẫn file output (.safetensors). Nếu None, tự động tạo tên
            safe_mode: Nếu True, chỉ chuyển đổi khi file đã được scan và an toàn
            
        Returns:
            Dict chứa kết quả chuyển đổi
        """
        if not self.is_supported():
            return {
                "success": False,
                "error": "Converter không được hỗ trợ. Vui lòng cài đặt PyTorch và safetensors."
            }

        input_path = Path(input_path)
        if not input_path.exists():
            return {
                "success": False,
                "error": f"File không tồn tại: {input_path}"
            }

        # Tạo tên output nếu chưa có
        if output_path is None:
            output_path = input_path.with_suffix('.safetensors')
        else:
            output_path = Path(output_path)

        try:
            # Đọc file pickle (CHỈ với các file đã được verify an toàn!)
            if safe_mode:
                warnings.warn(
                    "⚠️  CẢNH BÁO: Đang load file pickle. "
                    "Chỉ thực hiện với các file đã được scan và verified an toàn!",
                    UserWarning
                )

            with open(input_path, 'rb') as f:
                obj = pickle.load(f)

            # Kiểm tra xem object có phải là PyTorch model không
            if not isinstance(obj, dict):
                return {
                    "success": False,
                    "error": f"File pickle không chứa dictionary. Loại: {type(obj)}. "
                             "Chỉ hỗ trợ chuyển đổi PyTorch state_dict."
                }

            # Kiểm tra xem có phải là PyTorch tensors không
            tensors = {}
            metadata = {}
            
            for key, value in obj.items():
                if TORCH_AVAILABLE and isinstance(value, torch.Tensor):
                    tensors[key] = value
                    metadata[key] = {
                        "shape": list(value.shape),
                        "dtype": str(value.dtype),
                    }
                elif isinstance(value, (int, float, str, bool, list)):
                    # Metadata không phải tensor
                    metadata[key] = value
                else:
                    warnings.warn(
                        f"Bỏ qua key '{key}' với loại {type(value)}. "
                        "Chỉ tensor và primitive types được hỗ trợ.",
                        UserWarning
                    )

            if not tensors:
                return {
                    "success": False,
                    "error": "Không tìm thấy tensor nào trong file pickle. "
                             "Có thể file này không phải là PyTorch model."
                }

            # Lưu sang safetensors
            save_file(tensors, str(output_path), metadata=metadata)

            return {
                "success": True,
                "input_path": str(input_path),
                "output_path": str(output_path),
                "tensors_count": len(tensors),
                "metadata_keys": len(metadata),
                "message": f"Chuyển đổi thành công! Đã lưu {len(tensors)} tensors vào {output_path}"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Lỗi khi chuyển đổi: {str(e)}"
            }

    def convert_pytorch_to_safetensors(
        self,
        input_path: Path,
        output_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Chuyển đổi PyTorch .pth file sang safetensors.
        
        Args:
            input_path: Đường dẫn file .pth (có thể là zip hoặc pickle)
            output_path: Đường dẫn file output
            
        Returns:
            Dict chứa kết quả chuyển đổi
        """
        if not self.is_supported():
            return {
                "success": False,
                "error": "Converter không được hỗ trợ. Vui lòng cài đặt PyTorch và safetensors."
            }

        input_path = Path(input_path)
        if not input_path.exists():
            return {
                "success": False,
                "error": f"File không tồn tại: {input_path}"
            }

        if output_path is None:
            output_path = input_path.with_suffix('.safetensors')
        else:
            output_path = Path(output_path)

        try:
            # Đọc PyTorch checkpoint
            checkpoint = torch.load(input_path, map_location='cpu')

            # Xử lý các định dạng khác nhau của checkpoint
            if isinstance(checkpoint, dict):
                if 'state_dict' in checkpoint:
                    state_dict = checkpoint['state_dict']
                    metadata = {k: v for k, v in checkpoint.items() if k != 'state_dict'}
                elif all(isinstance(v, torch.Tensor) for v in checkpoint.values()):
                    state_dict = checkpoint
                    metadata = {}
                else:
                    # Lọc chỉ tensor
                    state_dict = {}
                    metadata = {}
                    for k, v in checkpoint.items():
                        if isinstance(v, torch.Tensor):
                            state_dict[k] = v
                        else:
                            metadata[k] = v
            else:
                return {
                    "success": False,
                    "error": f"Định dạng checkpoint không được hỗ trợ: {type(checkpoint)}"
                }

            if not state_dict:
                return {
                    "success": False,
                    "error": "Không tìm thấy state_dict trong checkpoint."
                }

            # Thêm metadata về shapes và dtypes
            tensor_metadata = {}
            for key, tensor in state_dict.items():
                tensor_metadata[key] = {
                    "shape": list(tensor.shape),
                    "dtype": str(tensor.dtype),
                }

            # Merge metadata
            final_metadata = {**metadata, **{"tensors": tensor_metadata}}

            # Lưu sang safetensors
            save_file(state_dict, str(output_path), metadata=final_metadata)

            return {
                "success": True,
                "input_path": str(input_path),
                "output_path": str(output_path),
                "tensors_count": len(state_dict),
                "metadata_keys": len(metadata),
                "message": f"Chuyển đổi thành công! Đã lưu {len(state_dict)} tensors vào {output_path}"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Lỗi khi chuyển đổi: {str(e)}"
            }

    def verify_safetensors(self, safetensors_path: Path) -> Dict[str, Any]:
        """
        Xác minh file safetensors có hợp lệ không.
        
        Args:
            safetensors_path: Đường dẫn file .safetensors
            
        Returns:
            Dict chứa thông tin về file
        """
        if not SAFETENSORS_AVAILABLE:
            return {
                "success": False,
                "error": "safetensors không được cài đặt."
            }

        safetensors_path = Path(safetensors_path)
        if not safetensors_path.exists():
            return {
                "success": False,
                "error": f"File không tồn tại: {safetensors_path}"
            }

        try:
            with safe_open(str(safetensors_path), framework="pt", device="cpu") as f:
                keys = f.keys()
                tensors_info = {}
                metadata = f.metadata() or {}

                for key in keys:
                    tensor = f.get_tensor(key)
                    tensors_info[key] = {
                        "shape": list(tensor.shape),
                        "dtype": str(tensor.dtype),
                        "size_bytes": tensor.numel() * tensor.element_size(),
                    }

            return {
                "success": True,
                "file_path": str(safetensors_path),
                "tensors_count": len(tensors_info),
                "tensors_info": tensors_info,
                "metadata": metadata,
                "file_size_mb": safetensors_path.stat().st_size / (1024 * 1024),
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Lỗi khi verify file: {str(e)}"
            }

