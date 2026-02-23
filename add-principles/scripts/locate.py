#!/usr/bin/env python3
"""
add-principles 原则库定位脚本

跨平台查找 principles.md 文件位置。
按优先级顺序尝试多种策略，返回 JSON 格式的结果。

Usage:
    python locate.py

Output:
    成功: {"success": true, "path": "/path/to/principles.md", "found_via": "strategy_name"}
    失败: {"success": false, "error": "错误信息", "checked_paths": [...]}
"""

import json
import os
import sys
from pathlib import Path

# ============ 配置常量 ============
ENV_VAR_NAME = "ADD_PRINCIPLES_PATH"
CONFIG_FILE_NAME = "config.toml"
DEFAULT_SKILL_NAME = "add-principles"
TARGET_FILE = "principles.md"


# ============ 工具函数 ============

def get_platform_default_skills_dir():
    """
    获取平台默认的 skills 目录
    
    Returns:
        Path: 默认 skills 目录路径
    """
    if sys.platform == "win32":
        # Windows: %USERPROFILE%\.kimi\skills
        home = Path(os.environ.get("USERPROFILE", ""))
    else:
        # macOS / Linux: ~/.kimi/skills
        home = Path.home()
    
    return home / ".kimi" / "skills"


def parse_toml_value(content, key):
    """
    简单解析 TOML 内容，提取指定 key 的值
    
    Args:
        content: TOML 文件内容字符串
        key: 要查找的 key
        
    Returns:
        str | None: key 的值，未找到返回 None
    """
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith(f"{key}") or f".{key}" in line.split("=")[0]:
            if "=" in line:
                # 提取等号后的值
                value = line.split("=", 1)[1].strip()
                # 去除引号
                value = value.strip('"').strip("'")
                return value
    return None


def check_principles_exists(base_path):
    """
    检查指定路径下是否存在 principles.md
    
    Args:
        base_path: Skill 基础目录或 principles.md 直接路径
        
    Returns:
        Path | None: 存在的 principles.md 路径，不存在返回 None
    """
    # 如果直接指向文件
    if base_path.name == TARGET_FILE and base_path.is_file():
        return base_path
    
    # 如果指向目录，检查目录下的 principles.md
    if base_path.is_dir():
        principles_path = base_path / TARGET_FILE
        if principles_path.is_file():
            return principles_path
    
    return None


# ============ 策略函数 ============

def strategy_env_override():
    """
    优先级 1: 环境变量覆盖
    
    用户可以通过设置 ADD_PRINCIPLES_PATH 完全自定义原则库位置。
    
    Returns:
        tuple: (strategy_name, path | None, error_message | None)
    """
    env_path = os.environ.get(ENV_VAR_NAME)
    
    if not env_path:
        return ("env", None, None)
    
    path = Path(env_path).expanduser().resolve()
    
    if not path.exists():
        return ("env", None, f"环境变量 {ENV_VAR_NAME} 指向的路径不存在: {path}")
    
    result = check_principles_exists(path)
    if result:
        return ("env", result, None)
    
    return ("env", None, f"环境变量 {ENV_VAR_NAME} 路径下未找到 {TARGET_FILE}: {path}")


def strategy_config_file():
    """
    优先级 2: Kimi 配置文件
    
    读取 ~/.kimi/config.toml 中的 skills_dir 配置。
    
    Returns:
        tuple: (strategy_name, path | None, error_message | None)
    """
    if sys.platform == "win32":
        config_home = Path(os.environ.get("USERPROFILE", "")) / ".kimi"
    else:
        config_home = Path.home() / ".kimi"
    
    config_path = config_home / CONFIG_FILE_NAME
    
    if not config_path.exists():
        return ("config", None, None)  # 静默失败，继续下一策略
    
    try:
        content = config_path.read_text(encoding="utf-8")
        skills_dir_str = parse_toml_value(content, "skills_dir")
        
        if not skills_dir_str:
            return ("config", None, None)
        
        skills_dir = Path(skills_dir_str).expanduser().resolve()
        skill_path = skills_dir / DEFAULT_SKILL_NAME
        
        result = check_principles_exists(skill_path)
        if result:
            return ("config", result, None)
        
        return ("config", None, f"配置的 skills_dir 中未找到: {skill_path}")
        
    except Exception as e:
        return ("config", None, f"读取配置文件失败: {e}")


def strategy_default_platform_path():
    """
    优先级 3: 平台默认路径
    
    使用 Kimi CLI 默认的安装位置。
    支持直接子目录和软连接两种情况。
    
    Returns:
        tuple: (strategy_name, path | None, error_message | None)
    """
    skills_dir = get_platform_default_skills_dir()
    skill_path = skills_dir / DEFAULT_SKILL_NAME
    
    # 检查直接子目录
    result = check_principles_exists(skill_path)
    if result:
        return ("default", result, None)
    
    # 检查软连接（skill-installer 安装方式）
    if skill_path.exists() or skill_path.is_symlink():
        try:
            # 解析软连接到真实路径
            real_path = skill_path.resolve()
            result = check_principles_exists(real_path)
            if result:
                return ("default", result, None)
        except Exception:
            pass
    
    # 尝试模糊匹配（如 add-principles-kimi、add-principles-main 等）
    if skills_dir.exists():
        for item in skills_dir.iterdir():
            if item.is_dir() or item.is_symlink():
                if DEFAULT_SKILL_NAME in item.name:
                    result = check_principles_exists(item)
                    if result:
                        return ("default", result, None)
    
    return ("default", None, f"默认路径中未找到: {skill_path}")


def strategy_cwd_fallback():
    """
    优先级 4: 当前目录回退（开发调试场景）
    
    用于 Skill 开发时直接在当前目录运行测试。
    
    Returns:
        tuple: (strategy_name, path | None, error_message | None)
    """
    cwd = Path.cwd()
    
    # 尝试 ./add-principles/principles.md
    skill_path = cwd / DEFAULT_SKILL_NAME
    result = check_principles_exists(skill_path)
    if result:
        return ("cwd", result, None)
    
    # 尝试当前目录就是 principles.md
    direct_file = cwd / TARGET_FILE
    if direct_file.exists():
        return ("cwd", direct_file, None)
    
    # 尝试父目录（如从 scripts/ 目录运行）
    parent = cwd.parent
    if (parent / TARGET_FILE).exists():
        return ("cwd", parent / TARGET_FILE, None)
    
    return ("cwd", None, f"当前目录及其子目录中未找到: {cwd}")


# ============ 主逻辑 ============

def locate():
    """
    执行查找，返回结果字典
    
    Returns:
        dict: 包含 success、path、found_via 等字段的结果字典
    """
    strategies = [
        strategy_env_override,
        strategy_config_file,
        strategy_default_platform_path,
        strategy_cwd_fallback,
    ]
    
    checked_paths = []
    
    for strategy_func in strategies:
        strategy_name, path, error = strategy_func()
        
        checked_paths.append({
            "strategy": strategy_name,
            "path": str(path) if path else None,
            "found": path is not None,
            "error": error
        })
        
        if path:
            return {
                "success": True,
                "path": str(path),
                "found_via": strategy_name,
                "checked_paths": checked_paths
            }
    
    # 所有策略都失败
    errors = [p for p in checked_paths if p.get("error")]
    
    return {
        "success": False,
        "error": "无法找到 principles.md，所有查找策略均未成功",
        "checked_paths": checked_paths,
        "suggestion": (
            "请确认 add-principles Skill 已正确安装。\n"
            "如需自定义原则库位置，请设置环境变量:\n"
            f"  export {ENV_VAR_NAME}=/path/to/principles.md"
        ),
        "errors_detail": errors
    }


def main():
    """入口函数，输出 JSON"""
    try:
        result = locate()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0 if result.get("success") else 1)
    except Exception as e:
        error_result = {
            "success": False,
            "error": f"定位脚本执行异常: {e}",
            "suggestion": "请检查 Python 版本 >= 3.6，并确认 locate.py 文件完整"
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
