import numbers
import os
from typing import Optional, List, Dict, Any

import time

from maa.context import Context
from maa.custom_recognition import CustomRecognition
from maa.job import Job
from pathlib import Path

from ..enum import *


def perform_team_management(context: Context, last_time_ref: list):
    """
    执行一次队伍管理，并更新时间戳（通过可变对象引用）
    :param context: MAA上下文
    :param last_time_ref: 传入 [last_team_manage_time] 列表，用于更新时间戳
    """
    try:
        print("[捉鬼任务] 立即执行队伍管理（因检测到组队需求）")
        if not open_team_interface_ZhuoGui(context):
            return False
        team_management(context)
        last_time_ref[0] = time.time()  # 更新外部的时间戳
        print("[捉鬼任务] 队伍管理完成")
        return True
    except Exception as e:
        print(f"[捉鬼任务] 队伍管理异常: {e}")
        popup(context)


def ClaimZhuoGuiTask(context):
    """打开活动界面"""
    while True:
        if enter_activity_interface(
                context,
                {"key": [57, 31]},
                "场景/活动界面",
                roi=[430, 26, 393, 55]
        ):
            print("[捉鬼任务] 进入活动界面成功")
            break  # 成功进入活动界面，退出循环
        # 主界面或活动界面识别失败，开始检测并处理弹窗和相关任务
        print("[捉鬼任务] 检测弹窗")
        popup(context)

        print("[捉鬼任务] 弹窗处理完成，重新尝试进入活动界面...")
    # 找到捉鬼任务并点击
    go_Zhong_Kui(context)
    # 检查到达钟馗场景
    templateMatching(context, image(context), "捉鬼任务/钟馗场景.png")
    # 领取任务
    identify_and_click(context, "捉鬼任务/开启捉鬼任务.png")

    if identify_and_click(context, "捉鬼任务/领取抓鬼任务成功.png"):
        return True
    # 检测调整队伍提醒
    return team_adjustment_reminder(context)


def team_adjustment_reminder(context: Context):
    if templateMatching(context, image(context), "捉鬼任务/调整队伍/提醒组队参加捉鬼任务"):
        return "提醒组队参加捉鬼任务"
    if templateMatching(context, image(context), "捉鬼任务/调整队伍/组队不足三人.png"):
        return "组队不足三人"
    if templateMatching(context, image(context), "捉鬼任务/调整队伍/调整队伍提醒"):
        return "调整队伍提醒"


def open_team_interface_ZhuoGui(context):
    TemporaryCount = 0
    while True:
        if enter_activity_interface(
                context,
                {"key": [57, 48]},
                "场景/队伍界面",
                # roi=[430, 26, 393, 55]
        ):
            print("[捉鬼任务] 进入队伍界面成功")
            return True  # 成功进入队伍界面，退出循环
        # 界面识别失败，开始检测并处理弹窗和相关任务
        if TemporaryCount > 2:
            return False
        print("[捉鬼任务] 检测弹窗")

        # 调用 check_baotu_task 处理弹窗或相关任务
        popup(context)

        print("[捉鬼任务] 弹窗处理完成，重新尝试进入活动界面...")


def team_management(context):
    while True:
        count = 0
        # 1. 检查是否创建队伍
        if not check_team_created(context):
            print("[捉鬼任务] 未创建队伍，正在创建队伍...")
            identify_and_click(context, "组队状态/创建队伍")
            # 等待队伍创建完成
            time.sleep(1)

        # 2. 检查当前目标状态
        print("[捉鬼任务] 检查当前目标状态...")
        current_target = check_goals_status(context, "组队状态/目标")

        # 3. 如果当前目标不是捉鬼任务，切换目标
        if current_target == 2:
            break
        count += 1
        if count == 2:
            popup(context)
            continue
        print("[捉鬼任务] 当前目标不是捉鬼任务，正在切换...")
        switch_to_ghost_hunt_target(context)
    while True:
        count = 0
        # 4. 检查并处理暂离队员
        print("[捉鬼任务] 检查暂离队员...")
        offline_members_exist = templateMatching(
            context,
            image(context),
            "组队状态/离线状态.png",
        )
        if offline_members_exist:
            print("[捉鬼任务] 发现暂离队员，正在处理...")
            offlineMembers(context)
        count += 1
        # 5. 检查队伍是否满人
        if check_team_full(context):
            exit_activity(context)
            break
        if count == 4:
            popup(context)
            continue


def go_Zhong_Kui(context: Context):
    swipe_count = 0
    while True:
        result = templateMatching(
            context,
            image(context),
            "捉鬼任务/捉鬼任务.png",
            threshold=0.8)
        if not result:
            swipe_count = activity_interface_sliding_rules(context, swipe_count=swipe_count)
            continue
        result_action = templateMatching(
            context,
            image(context),
            "捉鬼任务/参与按键",
            roi=[result["box"].x, result["box"].y, 400, 92],
            threshold=0.85
        )
        if result_action:
            actionOperation(
                context,
                "Click",
                param={
                    "target":
                        [
                            result_action["box"].x,
                            result_action["box"].y,
                            result_action["box"].w,
                            result_action["box"].h,
                        ]})
            time.sleep(10)
            break


def activity_interface_sliding_rules(context: Context, swipe_count):
    max_down_swipes = 3
    if swipe_count < max_down_swipes:
        print(f"[Tools] 向下滑动第 {swipe_count + 1} 次")
        swipe_down(context)
        swipe_count += 1
        time.sleep(1)
    elif swipe_count == max_down_swipes or swipe_count == max_down_swipes + 1:
        print("[Tools] 开始向上滑动")
        swipe_up(context)
        swipe_count += 1
        time.sleep(2)
    else:
        swipe_count = 0
        popup(context)
    return swipe_count


def InCatchGhosting(context: Context):
    templates = "战斗场景/检测到在战斗场景"
    roi = [1196, 610, 78, 62]
    result = templateMatching(context, image(context), templates, roi, 0.8)
    if result:
        return True
    return False


def check_team_created(context):
    """检查是否已创建队伍"""
    # 尝试查找退出队伍按钮，如果找到说明已创建队伍
    created_team = templateMatching(context, image(context), "组队状态/退出队伍.png")
    return created_team is not None


def switch_to_ghost_hunt_target(context):
    """切换到捉鬼任务目标"""
    # 点击切换目标按键
    identify_and_click(context, "组队状态/切换目标.png")

    # 等待调整目标界面出现
    target_interface_shown = templateMatching(
        context,
        image(context),
        "组队状态/调整目标界面.png",
    )

    if target_interface_shown:
        # 点击日常任务
        identify_and_click(context, "组队状态/日常任务.png", threshold=0.85)
        # 点击捉鬼任务
        identify_and_click(context, "组队状态/捉鬼任务.png", threshold=0.85)
        # 点击确认
        identify_and_click(context, "组队状态/确定", threshold=0.85)
        print("已切换到捉鬼任务目标")
    else:
        print("调整目标界面未找到")


def check_matching_status(context):
    """检查当前是否正在匹配"""
    # 这里需要根据你的实际逻辑来判断是否正在匹配
    # 假设通过检查某个UI元素来判断
    matching_ui = templateMatching(
        context,
        image(context),
        "组队状态/自动匹配.png",  # 需要你提供对应的模板图片
    )
    return matching_ui is not None


def start_auto_matching(context):
    """开始自动匹配"""
    identify_and_click(context, "组队状态/自动匹配.png", threshold=0.85)


def check_team_full(context):
    """检查队伍是否满人"""

    # 检查助战图标，如果不存在说明队伍满人
    if not templateMatching(
            context,
            image(context),
            "组队状态/助战.png",
            threshold=0.85
    ):
        return True

    # 可选：添加超时机制，避免无限循环
    # if timeout_condition:
    #     print("等待队伍满人超时")
    #     return False
    # 5. 检查当前是否正在匹配
    # print("检查匹配状态...")
    if check_matching_status(context):
        print("未在匹配状态，开始自动匹配...")
        start_auto_matching(context)
    # 短暂等待后再次检查
    time.sleep(15)
    return False


def offlineMembers(context: Context):
    member_rois = [
        [337, 153, 189, 466],  # 队员2
        [529, 153, 189, 466],  # 队员3
        [722, 153, 189, 466],  # 队员4
        [927, 162, 172, 452]  # 队员5
    ]
    for i, roi in enumerate(member_rois, start=2):
        identify_and_click(context, "组队状态/离线状态.png", roi=roi)
        identify_and_click(context, "捉鬼任务/请离队伍.png")


def check_goals_status(context: Context, template) -> numbers:
    temporaryDic = {}
    count = 0
    template_paths = get_all_png_files(template)
    for template_path in template_paths:
        count += 1
        mark = templateMatching(
            context,
            image(context),
            template_path,
        )
        if mark is not None:
            mark = "mark"
        temporaryDic[count] = mark
    # 获取所有值为"mark"的键
    matching_keys = [key for key, value in temporaryDic.items() if value == "mark"]

    # 如果只需要第一个匹配的键
    if matching_keys:
        first_match = matching_keys[0]
        return first_match
    return 0


def identify_and_click(context: Context, templates, roi: Optional[List[int]] = None, threshold: float = 0.7):
    result = templateMatching(
        context,
        image(context),
        templates,
        threshold=threshold,
        roi=roi
    )
    if result is not None:
        actionOperation(
            context,
            "Click",
            param={"target": [result["box"].x, result["box"].y, result["box"].w, result["box"].h]})
        time.sleep(1)
        return True
    return False


def search_unfinished_task(context: Context, current_node):
    swipe_count = 0
    while True:
        # === 获取最新截图 ===
        # ✅ 新增逻辑：如果检测到“已完成宝图任务”，说明无需再找，先退出再结束
        result = templateMatching(context,
                                  image(context),
                                  ["宝图任务/宝图任务 (1).png",
                                   "宝图任务/宝图任务 (2).png",
                                   "宝图任务/宝图任务 (3).png",
                                   "宝图任务/宝图任务 (4).png"
                                   ],
                                  roi=[308, 77, 845, 441],
                                  threshold=0.9)
        print("[宝图任务] 检测到【宝图任务】")
        if result:
            if templateMatching(context,
                                image(context),
                                ["宝图任务/已完成 (1).png",
                                 "宝图任务/已完成 (2).png"],
                                roi=[result["box"].x, result["box"].y, 400, 92],
                                threshold=0.8):
                # 先执行退出
                exit_activity(context)
                # 再跳转到 failure_next（通常是 "结束"）
                print("[宝图任务] 已退出活动界面，准备跳转到结束节点")
                context.override_next(name=current_node, next_list=["结束"])
                count = "A"
                break
            time.sleep(1.5)
            # 检查未完成任务
            result_action = templateMatching(
                context,
                image(context),
                ["宝图任务/参与按键 (1).png",
                 "宝图任务/参与按键 (2).png",
                 ],
                roi=[result["box"].x, result["box"].y, 400, 92],
                threshold=0.85
            )
            if result_action:
                actionOperation(context,
                                "Click",
                                param={
                                    "target": [result_action["box"].x,
                                               result_action["box"].y,
                                               result_action["box"].w,
                                               result_action["box"].h
                                               ]
                                })
                time.sleep(10)
                count = "B"
                break
        time.sleep(0.5)
        # 未找到，开始滑动
        swipe_count = activity_interface_sliding_rules(context, swipe_count=swipe_count)
    if count == "A":
        return True
    elif count == "B":
        return False


def find_resource_root(start_path: Path) -> Path:
    current = start_path.resolve()
    # print(f"🔍 开始查找 resource 目录，起始位置: {current}")

    while len(current.parts) > 1:
        potential_resource = current / "resource"
        if potential_resource.is_dir():
            # print(f"🎉 找到 resource 目录: {potential_resource}")
            return potential_resource
        parent = current.parent
        if current == parent:
            break
        current = parent
    # raise FileNotFoundError("❌ 未找到 'resource' 目录")


def get_all_png_files(templates):
    RESOURCE_DIR = find_resource_root(Path("."))
    if isinstance(templates, str):
        templates = [templates]

        # 固定 base/image 为扫描根目录
    base_image_dir = RESOURCE_DIR / "base" / "image"
    # if not base_image_dir.is_dir():
    #     raise FileNotFoundError(f"❌ 未找到 base/image 目录: {base_image_dir}")

    result = []

    for path in templates:
        # 清理路径，去掉首尾 / \
        clean_path = str(path).strip("/\\")

        # 如果路径以 base/image 开头，去掉它，只保留后面部分
        if clean_path.lower().startswith("base/image/"):
            clean_path = clean_path[len("base/image/"):].strip("/\\")

        # 构造完整路径
        full_path = (base_image_dir / clean_path).resolve()

        if not full_path.exists():
            # print(f"[警告] 路径不存在（相对于 base/image）: {clean_path}")
            continue

        try:
            rel_part = full_path.relative_to(base_image_dir)
        except ValueError:
            # print(f"[警告] 路径不在 base/image 下: {full_path}")
            continue

        if full_path.is_file():
            if full_path.suffix.lower() == '.png':
                result.append(str(rel_part.as_posix()))
        elif full_path.is_dir():
            # 递归扫描所有 .png 文件
            for png_file in full_path.rglob("*.png"):
                if png_file.is_file():
                    try:
                        inner_rel = png_file.relative_to(base_image_dir)
                        result.append(str(inner_rel.as_posix()))
                    except ValueError:
                        continue  # 不在 base/image 下

    return sorted(set(result))  # 去重 + 排序


def InTreasureHunting(context: Context):
    # 检测是否在宝图寻宝中
    templates = "战斗场景/检测到在战斗场景"
    roi = [1196, 610, 82, 70]
    result = templateMatching(context, image(context), templates, roi, 0.8)
    if result:
        print("[在寻宝中...]")
        import time
        time.sleep(300)
        return True
    return False


def TaskBar_ZhuoGuiTask(context: Context):
    import time
    for attempt in range(2):
        result = templateMatching(context, image(context), "捉鬼任务/捉鬼图标", roi=[1036, 107, 242, 402])
        if result:
            box = result["box"]
            target = [box.x, box.y, 5, 5]
            actionOperation(context, "Click", {"target": target})
            actionOperation(context, "Click", {"target": target})

            time.sleep(10)
            return True
        if attempt == 0:
            identify_and_click(
                context,
                "捉鬼任务/任务栏-暗",
                threshold=0.999,
                roi=[
                    1050,
                    100,
                    100,
                    55
                ])
            # 打开右上角地图
            # actionOperation(context, "Click", {"target": [7, 10, 70, 71]})
            # # 验证地图界面
            # if templateMatching(context, image(context), "map/地图标识.png", roi=[110, 35, 75, 70]):
            #     identify_and_click(context, "map/化生寺.png")
            # time.sleep(1)
    return False


def Taskbar_BaoTuTask(context: Context):
    # 检测任务栏的宝图任务图标
    templates = [
        "宝图任务/宝图任务图标 (1).png",
        "宝图任务/宝图任务图标 (2).png"
    ]
    roi = [1036, 107, 242, 402]

    for attempt in range(2):
        result = templateMatching(context, image(context), templates, roi, threshold=0.8)
        if result:
            print("[检测到任务栏有宝图任务]")
            box = result["box"]
            target = [box.x, box.y, 5, 5]
            actionOperation(context, "Click", {"target": target})
            actionOperation(context, "Click", {"target": target})
            time.sleep(10)
            return True

        # 第一次失败后才点击干扰项（第二次不再点）
        if attempt == 0:
            identify_and_click(context, "捉鬼任务/任务栏-暗", threshold=0.85)
            time.sleep(1)

    return False


def click_dianxiaoer(context):
    # 点击店小二
    actionOperation(context, "Click", {"target": [745, 364, 83, 32]})
    print("[宝图任务] 点击店小二")
    import time
    time.sleep(10)


def check_dianxiaoer_level(context: Context):
    # 检测是否在店小二场景
    result = templateMatching(
        context,
        image(context),
        "宝图任务/店小二场景.png",
        threshold=0.8
    )
    if result:
        print("[宝图任务] 在店小二场景")
        return True
    return False


def claim_the_task(context: Context):
    # 领取宝图任务
    result = templateMatching(
        context,
        image(context),
        [
            "宝图任务/领取宝图任务 (1).png",
            "宝图任务/领取宝图任务 (2).png"
        ],
        threshold=0.8
    )
    print(result)
    if result:
        actionOperation(
            context,
            "Click",
            {"target": [
                result["box"].x + result["box"].w // 4,
                result["box"].y + result["box"].h // 4,
                result["box"].w // 2,
                result["box"].h // 2
            ]
            }
        )
        print("[宝图任务] 领取宝图任务")
        return True
    return False


def check_zhuogui_task(context: Context, current_count):
    if TaskBar_ZhuoGuiTask(context):
        if InCatchGhosting(context):
            return ZhuoGuiState.IN_BATTLE, current_count
    if InCatchGhosting(context):
        return ZhuoGuiState.IN_BATTLE, current_count
        # 检测“继续捉鬼”弹窗 → 本轮结束
    if templateMatching(context, image(context), "捉鬼任务/继续捉鬼提醒.png", roi=[386, 238, 517, 246]):
        identify_and_click(context, "组队状态/确定", roi=[386, 238, 517, 246])
        new_count = current_count + 1
        print(f"完成第 {new_count} 轮捉鬼")
        return ZhuoGuiState.ROUND_COMPLETED, new_count

        # 弹窗处理
    popup_result = popup(context)
    print(f"弹窗处理完成，结果: {popup_result}")

    time.sleep(1)

    # 尝试领取任务
    result = ClaimZhuoGuiTask(context)
    if result is True:
        return check_zhuogui_task(context, current_count)
    elif result in ["提醒组队参加捉鬼任务", "组队不足三人"]:
        # 触发队伍管理（但不在这里执行，由主循环控制）
        return ZhuoGuiState.NEED_TEAM, current_count
    elif result == "调整队伍提醒":
        identify_and_click(context, "捉鬼任务/调整队伍/取消", roi=[386, 238, 517, 246])
        return ZhuoGuiState.IDLE, current_count
    return ZhuoGuiState.IDLE, current_count


def check_baotu_task(context, current_node):
    if Taskbar_BaoTuTask(context):
        if InTreasureHunting(context):
            print("正在寻宝中...")
            while True:
                if enter_activity_interface(
                        context,
                        {"key": [57, 31]},
                        "场景/活动界面",
                        roi=[430, 26, 393, 55]
                ):
                    print("[宝图任务] 进入活动界面成功")
                    break  # 成功进入活动界面，退出循环
            search_unfinished_task(context, current_node)
            return CustomRecognition.AnalyzeResult(box=None, detail="all tasks completed and exited")
    # 单独检测宝图状态（如果没有宝图任务但有宝图状态）
    if InTreasureHunting(context):
        while True:
            if enter_activity_interface(
                    context,
                    {"key": [57, 31]},
                    "场景/活动界面",
                    roi=[430, 26, 393, 55]
            ):
                print("[宝图任务] 进入活动界面成功")
                break  # 成功进入活动界面，退出循环
        search_unfinished_task(context, current_node)
        return CustomRecognition.AnalyzeResult(box=None, detail="all tasks completed and exited")

    # 处理弹窗
    popup_result = popup(context)
    print(f"弹窗处理完成，结果: {popup_result}")

    # 添加短暂延迟，避免过于频繁的检测
    time.sleep(1)


# 检测弹窗
def popup(context: Context):
    # 获取当前屏幕截图
    # === 获取最新截图 ===
    # === 检测弹窗 ===
    # 检测是否在弹窗中
    if not templateMatching(context, image(context), "base/image/弹窗"):
        return False
    print("[检测有弹窗]")
    exiticon = templateMatching(context, image(context), "base/image/ExitIcon", [777, 1, 503, 327], 0.7, )
    if not exiticon:
        return False
    actionOperation(context,
                    "click",
                    param={
                        "target": [exiticon.get("reco_detail").x + exiticon.get("reco_detail").w // 4,
                                   exiticon.get("reco_detail").y + exiticon.get("reco_detail").h // 4,
                                   exiticon.get("reco_detail").w // 2,
                                   exiticon.get("reco_detail").h // 2
                                   ]
                    }
                    )
    return True


def image(context: Context):
    # 获取当前屏幕截图
    job = context.tasker.controller.post_screencap()
    job.wait()
    # === 获取最新截图 ===
    current_image = context.tasker.controller.cached_image  # ✅ 最新图像
    return current_image


def _load_templates_from_directory(directory_path: str) -> List[str]:
    template_paths = []
    full_path = os.path.join("resource", directory_path)

    if not os.path.exists(full_path):
        print(f"[QuickExitRecognizer] 警告: 模板目录不存在: {full_path}")
        return template_paths

    # 递归遍历目录，收集所有PNG图片的相对路径
    for root, dirs, files in os.walk(full_path):
        for filename in files:
            if filename.lower().endswith(".png"):
                # 获取相对于 resource 目录的完整路径
                absolute_path = os.path.join(root, filename)

                # 转换为相对于 resource 目录的路径
                relative_path = os.path.relpath(absolute_path, "resource")

                template_paths.append(relative_path)
    print(f"[QuickExitRecognizer] 已找到 {len(template_paths)} 个模板图片")

    # 打印前几个路径作为示例
    for path in template_paths:
        print(f"  - {path}")
    print(f"  - ... 还有 {len(template_paths)} 个")

    return template_paths


"""向下滑动"""


def swipe_down(context: Context):
    job: Job = context.tasker.controller.post_swipe(868, 448, 868, 148, 500)
    job.wait()


"""向上滑动"""


def swipe_up(context: Context):
    job: Job = context.tasker.controller.post_swipe(868, 145, 868, 448, 600)
    job.wait()


"""确保进入活动界面"""


def enter_activity_interface(
        context: Context,
        param: Dict = None,
        templates=None,
        roi: Optional[List[int]] = None) -> bool:
    if templates is None:
        templates = []
    for i in range(3):
        print(f"[Tools] 尝试进入界面 (第 {i + 1}/3 次)")
        actionOperation(context, "ClickKey", param)

        # ✅ 等待界面响应
        time.sleep(1.5)

        if templateMatching(
                context,
                image(context),
                templates,
                threshold=0.7,
                roi=roi
        ):
            return True

        time.sleep(1.0)
    templateMatching(context, image(context), ["base/image/场景/主界面"])

    print("[Tools] 尝试 3 次后仍无法进入界面")
    return False


"""退出活动界面"""


def exit_activity(context: Context):
    reco_detail = templateMatching(context, image(context), "ExitIcon", threshold=0.8)
    box = reco_detail.get("box")
    center_x = box.x + box.w // 2
    center_y = box.y + box.h // 2
    click_pipeline = {
        "actionClickKey": {
            "action": {
                "type": "Click",
            }
        }
    }
    context.run_action(
        "actionClickKey",  # entry
        (center_x, center_y, 5, 5),  # box: 矩形区域
        "",  # reco_detail 留空
        click_pipeline,  # pipeline_override
    )
    # ✅ 等待界面响应
    time.sleep(1.5)


def actionOperation(context, action_type, param: Dict = None, match_result: Dict = None):
    if param is None:
        param = {}
        # 确定box参数
    if match_result and "box" in match_result:
        box = match_result["box"]  # 使用匹配结果的box
    else:
        box = (0, 0, 0, 0)  # 默认全屏
    click_pipeline = {
        "actionClickKey": {
            "action": {
                "type": action_type,
                "param": param
            }
        }
    }
    context.run_action(
        "actionClickKey",  # entry
        box,  # box: 矩形区域
        "",  # reco_detail 留空
        click_pipeline,  # pipeline_override
    )
    # ✅ 等待界面响应
    time.sleep(1.5)


def templateMatching(
        context: Context,
        update_screenshot,
        templates,
        roi: Optional[List[int]] = None,
        threshold: float = 0.7,
        method: int = 5
) -> Optional[Dict[str, Any]]:
    """
    通用模板匹配函数

    Args:
        context: MAA Context对象
        update_screenshot: 图像数据
        templates: 模板路径，可以是单个字符串或字符串列表
        roi: 感兴趣区域 [x, y, w, h]
        threshold: 匹配阈值
        method: 模板匹配方法

    Returns:
        匹配结果字典或None
    """
    # 确保 templates 是列表
    template_paths = get_all_png_files(templates)

    final_roi = roi or [0, 0, 0, 0]

    print(f"[Tools] 开始匹配，模板数量: {len(template_paths)}")

    # 用于保存成功匹配的结果
    matched_template_path = None
    matched_reco_detail = None

    for template_path in template_paths:
        time.sleep(0.2)  # 减少等待时间

        # 构造动态 pipeline - 注意参数顺序正确
        pipeline_override = {
            "DynamicTemplateNode": {
                "recognition": {
                    "type": "TemplateMatch",
                    "param": {
                        "template": template_path,
                        "threshold": threshold,  # 阈值应该是数字
                        "roi": final_roi,  # ROI 应该是数组
                        "method": method
                    }
                }
            }
        }

        print(f"[Tools] 尝试模板: {template_path}")

        # 执行识别
        try:
            reco_detail = context.run_recognition(
                entry="DynamicTemplateNode",
                image=update_screenshot,
                pipeline_override=pipeline_override
            )
        except Exception as e:
            print(f"[Tools] 模板 {template_path} 匹配异常: {e}")
            continue

        # 检查是否匹配成功
        if reco_detail and hasattr(reco_detail, 'box') and reco_detail.box:
            score = reco_detail.best_result.score if hasattr(reco_detail, 'best_result') else 0
            # print(f"[Tools] 模板 '{template_path}' 匹配成功，得分: {score}")

            matched_reco_detail = reco_detail
            matched_template_path = template_path
            break
        # else:
        # print(f"[Tools] 模板 '{template_path}' 匹配失败")

    # 处理最终结果
    if matched_reco_detail:
        score = (
            matched_reco_detail.best_result.score
            if hasattr(matched_reco_detail, 'best_result') and matched_reco_detail.best_result
            else 0.0
        )
        box = matched_reco_detail.box

        result = {
            "box": box,
            "score": float(score),
            "template_path": matched_template_path,
            "reco_detail": matched_reco_detail,
        }
        print(
            f"[Tools] 匹配成功！模板: {matched_template_path}, "
            f"[Tools] 位置: {box}, 得分: {score:.3f}"
        )
        return result

    print("[Tools] 所有模板均未匹配成功")
    return None  # 明确返回 None
