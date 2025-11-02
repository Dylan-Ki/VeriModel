rule dangerous_pickle_os_system
{
    meta:
        description = "Phát hiện os.system (kỹ thuật phổ biến nhất)"
        severity = "HIGH"
    strings:
        $opcode_global = "c" // opcode GLOBAL
        $module_os = "os"
        $func_system = "system"
    condition:
        $opcode_global and $module_os and $func_system
}

rule dangerous_pickle_subprocess
{
    meta:
        description = "Phát hiện module subprocess (Popen, run, call)"
        severity = "HIGH"
    strings:
        $opcode_global = "c"
        $module_subprocess = "subprocess"
        $func_popen = "Popen"
        $func_run = "run"
        $func_call = "call"
    condition:
        $opcode_global and $module_subprocess and ($func_popen or $func_run or $func_call)
}

rule dangerous_pickle_obfuscation
{
    meta:
        description = "Phát hiện các kỹ thuật che giấu (eval, exec, __import__)"
        severity = "CRITICAL"
    strings:
        $eval = "eval"
        $exec = "exec"
        $import_obf = "__import__"
        $getattr = "getattr"
    condition:
        any of ($eval, $exec, $import_obf, $getattr)
}

rule dangerous_pickle_reduce
{
    meta:
        description = "Phát hiện opcode REDUCE, có thể được dùng để gọi hàm"
        severity = "MEDIUM"
    strings:
        $reduce = "R" // opcode REDUCE
    condition:
        $reduce
}

rule suspicious_pickle_network
{
    meta:
        description = "Phát hiện các module mạng (socket, urllib, requests)"
        severity = "MEDIUM"
    strings:
        $socket = "socket"
        $urllib = "urllib"
        $requests = "requests"
    condition:
        any of ($socket, $urllib, $requests)
}