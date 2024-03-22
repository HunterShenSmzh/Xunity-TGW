# Xunity-TGW
XUnity.AutoTranslator+Text Generation webui translate  
特别感谢[SakuraTranslator](https://github.com/fkiliver/SakuraTranslator)  
本项目是由其修改而来  
# 介绍
这是一个基于XUnity.AutoTranslator和Text Geneartion Webui的Unity游戏本地翻译器  
建议使用Sakura模型翻译日文 v0.9b https://huggingface.co/SakuraLLM/Sakura-13B-LNovel-v0.9b-GGUF/tree/main  
建议使用qwen模型翻译英文 https://huggingface.co/Qwen  
# 准备
首先参考XUnity.AutoTranslator文档部署XUnity.AutoTranslator：[XUnity.AutoTranslator](https://github.com/bbepis/XUnity.AutoTranslator)  
然后参考Text Geneartion Webui文档完成本地部署：[text-generation-webui](https://github.com/oobabooga/text-generation-webui)  
或者直接用b站的一键包,解压即用：[一键包](https://www.bilibili.com/video/BV1Te411U7me)  
# 流程
确保TGW成功加载模型并勾选api  

api启动  
![image](https://github.com/HunterShenSmzh/Xunity-TGW/assets/129963508/90761f02-17a5-41b3-b91e-4107f5134bb0)

模型加载完成  
![image](https://github.com/HunterShenSmzh/Xunity-TGW/assets/129963508/44b4b198-c6dd-4d92-bcf5-79864ff56c85)

从文件目录下载TGWTranslator.dll放置在Translators文件夹内

如果你使用ReiPatcher，你应该放在{游戏目录}\{游戏名}_Data\Managed\Translators   

如果你使用BepInEx,你应该放在{游戏目录}\BepInEx\plugins\XUnity.AutoTranslator\Translators   

修改AutoTranslatorConfig.ini  

如果你使用ReiPatcher，配置文件应该在`{游戏目录}\AutoTranslator\Config.ini  

如果你使用BepInEx,配置文件应该在`{游戏目录}\BepInEx\config\AutoTranslatorConfig.ini  

修改内容：  

[Service]  
Endpoint=TGWTranslator  
FallbackEndpoint=  

[General]  
Language=翻译完成的语言(如zh-CN)  
FromLanguage=你要翻译的语言(如jp,en)  

如果你在使用中出现了缺字、方块字等情况，请指定外部字体：  
[Behaviour]  
OverrideFont= ##填写你系统中已安装的字体名  
OverrideFontTextMeshPro= arialuni_sdf_u2018 ##或arialuni_sdf_u2019  
其中arialuni_sdf_u201x可以从字体文件获取，请解压后直接放置在游戏根目录  

启动游戏后，使用快捷键alt+0打开翻译面板，选择TGWTranslator  

![43fd697ac5f7d2faabee7485ca99abc0](https://github.com/HunterShenSmzh/Xunity-TGW/assets/129963508/199c76b4-c9a1-4a5c-9fbc-ac37f4023067)


![f646f4406622b4dbc1b720641d7e4b1d](https://github.com/HunterShenSmzh/Xunity-TGW/assets/129963508/e4bf5d2f-53f4-4b96-8f9f-fd4c2a5c6bcd)


