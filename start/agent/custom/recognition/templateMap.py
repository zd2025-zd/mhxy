import json

from maa.agent.agent_server import AgentServer
from maa.custom_recognition import CustomRecognition
from ..action.variable_manager import VariableStorage
from ..tools.functionTools import *


@AgentServer.custom_recognition("MyTemplateRecognition")
class MyTemplateRecognition(CustomRecognition):

    def analyze(
            self,
            context: Context,
            argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult:

        try:
            # 解析参数
            custom_param = json.loads(argv.custom_recognition_param)
            template = custom_param.get("template")
            print(f"template = {template}")
            map_config_json = VariableStorage.get("CURRENT_MAP_CONFIG")
            map_config = json.loads(map_config_json)
            tem = map_config.get(template)
            # 处理模板数组
            template_paths = []
            if isinstance(tem, list):
                # 如果是数组，遍历获取每个模板路径
                for tpl in tem:
                    template_path = tpl
                    if template_path:
                        template_paths.append(template_path)
                    else:
                        print(f"[MyTemplateRecognition] 警告: 模板 '{tpl}' 未在配置中找到")
                print(f"template_paths = {template_paths}")
            else:
                # 单个模板的情况，保持向后兼容
                template_path = tem
                if template_path:
                    template_paths.append(template_path)

            if not template_paths:
                print("[MyTemplateRecognition] 错误: 未找到有效的模板路径")
                return CustomRecognition.AnalyzeResult(
                    box=(0, 0, 0, 0),
                    detail="No valid template paths found"
                )

            # print(f"template_paths={template_paths}")

            threshold = custom_param.get("threshold", 0.7)
            roi = custom_param.get("roi", [0, 0, 0, 0])
            method = custom_param.get("method", 5)
            name = custom_param.get("current_node_name")
            success_next = custom_param.get("success_next")
            failure_next = custom_param.get("failure_next")
            click_target = custom_param.get("click", False)

            # 遍历所有模板进行匹配
            matched_reco_detail = None
            matched_template_path = None

            for template_path in template_paths:
                # 检查模板文件是否存在（可选，根据需求开启）
                # if not os.path.exists(template_path):
                #     print(f"[MyTemplateRecognition] 警告: 模板文件不存在: {template_path}")
                #     continue

                result = templateMatching(context, image(context), template_path, roi, threshold, method)

                # 检查是否匹配成功
                if result["reco_detail"] and result["box"]:
                    matched_reco_detail = result.get("reco_detail")
                    matched_template_path = template_path
                    print(f"[MyTemplateRecognition] 模板 {template_path} 匹配成功")
                    break  # 找到一个匹配的就退出循环
                else:
                    print(f"[MyTemplateRecognition] 模板 {template_path} 匹配失败")

            # 处理匹配结果
            if matched_reco_detail:
                score = matched_reco_detail.best_result.score if hasattr(matched_reco_detail, 'best_result') else 0
                print(
                    f"模板匹配成功！使用的模板: {matched_template_path}, 位置: {matched_reco_detail.box}, 得分: {score:.3f}")

                # 如果配置了点击，则执行点击操作
                if click_target:
                    try:
                        # 计算点击中心点
                        box = matched_reco_detail.box
                        center_x = box.x + box.w // 2
                        center_y = box.y + box.h // 2
                        # 执行点击操作: (609, 425)

                        print(f"[MyTemplateRecognition] 执行点击操作: ({center_x}, {center_y})")

                        # 方法2：使用 run_action
                        actionOperation(context, "Click", {"target": [center_x, center_y, box.w // 2, box.h // 2]})
                        # print(f"[MyTemplateRecognition] 点击操作结果: {click_result}")

                    except Exception as e:
                        print(f"[MyTemplateRecognition] 点击操作异常: {e}")
                        import traceback
                        traceback.print_exc()

                # 设置下一步流程
                if name and success_next:
                    print(f"[MyTemplateRecognition] 设置成功跳转: {name} -> {success_next}")
                    context.override_next(name=name, next_list=[success_next])
                else:
                    print(f"[MyTemplateRecognition] 成功跳转参数缺失: name={name}, success_next={success_next}")

                # 返回成功结果
                return CustomRecognition.AnalyzeResult(
                    box=matched_reco_detail.box,
                    detail=f"Match success with template: {matched_template_path}, score: {score:.3f}",
                )
            else:
                print(f"所有模板匹配失败！共尝试了 {len(template_paths)} 个模板")

                # 设置下一步流程
                if name and failure_next:
                    print(f"[MyTemplateRecognition] 设置失败跳转: {name} -> {failure_next}")
                    context.override_next(name=name, next_list=[failure_next])
                else:
                    print(f"[MyTemplateRecognition] 失败跳转参数缺失: {name}, failure_next={failure_next}")
                # 关键：使用override_next来明确告诉任务控制器跳过当前节点
                # 设置next_list为空数组，表示跳过当前节点的所有后续流程
            return CustomRecognition.AnalyzeResult(
                box=(0, 0, 0, 0),
                detail=f"All {len(template_paths)} templates match failed, continue to next")

        except Exception as e:
            print(f"[MyTemplateRecognition] 分析过程中发生未知错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return CustomRecognition.AnalyzeResult(
                box=(0, 0, 0, 0),
                detail=f"Analysis Error: {str(e)}",
            )
