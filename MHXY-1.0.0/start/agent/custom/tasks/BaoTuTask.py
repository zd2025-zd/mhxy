import json

from maa.agent.agent_server import AgentServer
from maa.context import Context
from maa.custom_recognition import CustomRecognition

from ..tools.functionTools import *


@AgentServer.custom_recognition("BaoTuTask")
class BaoTuTask(CustomRecognition):

    def analyze(
            self,
            context: Context,
            argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult:
        param = json.loads(argv.custom_recognition_param)
        current_node = param.get("current_node")

        # ===主界面检查===

        # 检测主界面
        print(f"[宝图任务] 主界面")

        while True:
            # 获取最新画面
            if templateMatching(context, image(context), ["base/image/场景/主界面"]):
                print("[宝图任务] 已确认在主界面")
                break
            print("[宝图任务] 主界面识别失败，开始检测并处理弹窗")
            popup_result = popup(context)
            print(f"[宝图任务] 弹窗处理完成，结果: {popup_result}")
            print("[宝图任务] 重新检测主界面...")

        # === 1. 确保进入活动界面 ===
        print(f"[宝图任务] 进入活动界面")

        while True:
            if enter_activity_interface(
                    context,
                    {"key": [57, 31]},
                    "场景/活动界面",
                    roi=[430, 26, 393, 55]
            ):
                print("[宝图任务] 进入活动界面成功")
                break  # 成功进入活动界面，退出循环
            # 主界面或活动界面识别失败，开始检测并处理弹窗和相关任务
            print("[宝图任务] 检测弹窗")

            # 调用 check_baotu_task 处理弹窗或相关任务
            check_baotu_task(context, current_node)

            print("[宝图任务] 弹窗处理完成，重新尝试进入活动界面...")
        # === 主循环：查找未完成任务 ===
        task_finished = search_unfinished_task(context, current_node)
        if task_finished:
            # 已经 override_next 并应结束，直接返回空结果
            return CustomRecognition.AnalyzeResult(box=[0, 0, 0, 0], detail="task finished")
        # === 领取任务 ===

        print("[宝图任务] 开始检查店小二界面并领取任务")

        while True:
            # 第一步：检查是否在店小二界面
            if not check_dianxiaoer_level(context):
                print("[宝图任务] 未检测到店小二界面")
                check_baotu_task(context, current_node)
                time.sleep(1)  # 给画面恢复留时间
                continue  # 跳过下面的代码，重新开始循环

            # 第二步：尝试领取任务
            if not claim_the_task(context):
                print("[宝图任务] 没有领取任务")
                check_baotu_task(context, current_node)
                time.sleep(1)
                continue  # 重新开始循环（再次检查店小二 + 领取）

            # ✅ 两个条件都满足，跳出循环
            print("[宝图任务] 循环检测")
            check_baotu_task(context, current_node)
            break  # 退出循环，进入下一步

        return CustomRecognition.AnalyzeResult(box=[0, 0, 0, 0], detail="")
