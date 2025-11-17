# # test_png_scanner.py
# # 功能：扫描 resource/base/image 下所有 .png 文件，支持相对路径输入
#
# import os
# from pathlib import Path
#
# def find_resource_root(start_path: Path) -> Path:
#     """向上查找 resource 目录"""
#     current = start_path.resolve()
#     # print(f"🔍 开始查找 resource 目录，起始位置: {current}")
#
#     while len(current.parts) > 1:
#         potential_resource = current / "resource"
#         if potential_resource.is_dir():
#             # print(f"🎉 找到 resource 目录: {potential_resource}")
#             return potential_resource
#         parent = current.parent
#         if current == parent:
#             break
#         current = parent
#     # raise FileNotFoundError("❌ 未找到 'resource' 目录")
#
#
# def scan_png_files(templates):
#     """
#     扫描 resource/base/image 下指定路径中的所有 .png 文件
#     支持输入：
#         - "场景/主界面"
#         - "图标/活动图标 (1).png"
#         - "base/image/弹窗"（自动兼容）
#         - 或列表形式
#
#     输出：相对于 base/image 的路径，如 "弹窗/师门界面 (1).png"
#     """
#     if isinstance(templates, str):
#         templates = [templates]
#
#     # 固定 base/image 为扫描根目录
#     base_image_dir = RESOURCE_DIR / "base" / "image"
#     if not base_image_dir.is_dir():
#         raise FileNotFoundError(f"❌ 未找到 base/image 目录: {base_image_dir}")
#
#     result = []
#
#     for path in templates:
#         # 清理路径，去掉首尾 / \
#         clean_path = str(path).strip("/\\")
#
#         # 如果路径以 base/image 开头，去掉它，只保留后面部分
#         if clean_path.lower().startswith("base/image/"):
#             clean_path = clean_path[len("base/image/"):].strip("/\\")
#
#         # 构造完整路径
#         full_path = (base_image_dir / clean_path).resolve()
#
#         if not full_path.exists():
#             print(f"[警告] 路径不存在（相对于 base/image）: {clean_path}")
#             continue
#
#         try:
#             rel_part = full_path.relative_to(base_image_dir)
#         except ValueError:
#             print(f"[警告] 路径不在 base/image 下: {full_path}")
#             continue
#
#         if full_path.is_file():
#             if full_path.suffix.lower() == '.png':
#                 result.append(str(rel_part.as_posix()))
#         elif full_path.is_dir():
#             # 递归扫描所有 .png 文件
#             for png_file in full_path.rglob("*.png"):
#                 if png_file.is_file():
#                     try:
#                         inner_rel = png_file.relative_to(base_image_dir)
#                         result.append(str(inner_rel.as_posix()))
#                     except ValueError:
#                         continue  # 不在 base/image 下
#
#     return sorted(set(result))  # 去重 + 排序
#
#
# # =============================
# #        测试入口
# # =============================
# if __name__ == "__main__":
#     print("=" * 60)
#     print("🔍 PNG 文件扫描器 - 独立测试版")
#     print("📌 功能：自动扫描 resource/base/image 下所有 .png 文件")
#     print("💡 输入支持：'场景/主界面' 或 'base/image/...'，输出如：弹窗/师门界面 (1).png")
#     print("=" * 60)
#
#     print("📁 当前工作目录:", os.getcwd())
#     print()
#
#     try:
#         RESOURCE_DIR = find_resource_root(Path("."))
#     except FileNotFoundError as e:
#         print(e)
#         input("\n按回车键退出...")
#         exit(1)
#
#     print("-" * 60)
#
#     # ✅ 现在这三种写法都能正确识别
#     test_paths = [
#         "场景/主界面",
#         "图标/活动图标 (1).png",
#         "base/image/弹窗",
#         "弹窗"  # 也可以只写最后一级
#     ]
#
#     for user_path in test_paths:
#         print(f"📁 测试路径: {user_path}")
#         files = scan_png_files(user_path)
#
#         if files:
#             print(f"✅ 成功找到 {len(files)} 个 .png 文件:")
#             for file in files:
#                 print(f"   🖼️  {file}")
#         else:
#             print("❌ 未找到任何 .png 文件")
#
#         print("-" * 60)
#
#     print("✅ 所有测试完成！")
#     input("\n按回车键退出...")

"""
垒石体系        大乔  张机  鲁肃          孙权

攻其体系        曹纯  文鸯  张辽          马超  曹操

战磐体系        荀彧  程昱  郭嘉          马岱  马谡  马腾            关羽  张绣

马良同心        刘备  马良  夏侯惇

神赏体系        鬼吕  吕蒙  田丰


"""