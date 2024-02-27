﻿using Newtonsoft.Json;
using System;
using System.Collections;
using System.IO;
using System.Net;
using System.Text;
using XUnity.AutoTranslator.Plugin.Core.Endpoints;

namespace TGWTranslator
{
    public class TGWTranslatorEndpoint : ITranslateEndpoint
    {
        public string Id => "TGWTranslator";

        public string FriendlyName => "TGW Translator";

        public int MaxConcurrency => 1;

        public int MaxTranslationsPerRequest => 1;

        // params
        private string _endpoint;
        private string _apiType;

        public void Initialize(IInitializationContext context)
        {
            _endpoint = context.GetOrCreateSetting<string>("TGW", "Endpoint", "http://127.0.0.1:5000/v1/chat/completion");
            _apiType = context.GetOrCreateSetting<string>("TGW", "ApiType", string.Empty);
        }

        public IEnumerator Translate(ITranslationContext context)
        {
            var untranslatedText = context.UntranslatedText;

            // 以换行符分割文本
            string[] lines = untranslatedText.Split(new[] { "\r\n", "\r", "\n" }, StringSplitOptions.None);
            StringBuilder translatedTextBuilder = new StringBuilder();

            foreach (var line in lines)
            {
                if (!string.IsNullOrEmpty(line))
                {
                    // 逐行翻译
                    IEnumerator translateLineCoroutine = TranslateLine(line, translatedTextBuilder);
                    while (translateLineCoroutine.MoveNext())
                    {
                        yield return null;
                    }
                }
                else
                {
                    // 保留空行
                    translatedTextBuilder.AppendLine();
                }
            }

            string translatedText = translatedTextBuilder.ToString().TrimEnd('\r', '\n');
            context.Complete(translatedText);
        }

        private IEnumerator TranslateLine(string line, StringBuilder translatedTextBuilder)
        {
            // 构建请求JSON
            string json = MakeRequestJson(line);
            var dataBytes = Encoding.UTF8.GetBytes(json);

            HttpWebRequest request = (HttpWebRequest)WebRequest.Create(_endpoint);
            request.Method = "POST";
            request.ContentType = "application/json";
            request.ContentLength = dataBytes.Length;

            using (Stream requestStream = request.GetRequestStream())
            {
                requestStream.Write(dataBytes, 0, dataBytes.Length);
            }

            var asyncResult = request.BeginGetResponse(null, null);

            // 等待异步操作完成
            while (!asyncResult.IsCompleted)
            {
                yield return null;
            }

            string responseText;
            using (WebResponse response = request.EndGetResponse(asyncResult))
            {
                using (Stream responseStream = response.GetResponseStream())
                {
                    using (StreamReader reader = new StreamReader(responseStream))
                    {
                        responseText = reader.ReadToEnd();
                    }
                }
            }

            // 手动解析JSON响应
            var startIndex = responseText.IndexOf("\"content\":") + 10;
            var endIndex = responseText.IndexOf(",", startIndex);
            var translatedLine = responseText.Substring(startIndex, endIndex - startIndex).Trim('\"', ' ', '\r', '\n', '}', ']');
            if (translatedLine.EndsWith("<|im_end|>"))
            {
                translatedLine = translatedLine.Substring(0, translatedLine.Length - "<|im_end|>".Length);
            }

            // 将翻译后的行添加到StringBuilder
            translatedTextBuilder.AppendLine(translatedLine);
        }

        private string MakeRequestJson(string line)
        {
            string json;
            if (_apiType == "TGW")
            {
                var messages = new[]
                {
                    new { role = "system", content = "你是一个翻译模型，可以流畅通顺地将任何语言翻译成简体中文，并联系上下文正确使用人称代词，不擅自添加原文中没有的代词。" },
                    new { role = "user", content = $"将下面的文本翻译成中文：{line}" }
                };

                var payload = new
                {
                    messages = messages,
                    temperature = 0.6,
                    stop = new string[] { "\n###", "\n\n", "[PAD151645]", "<|im_end|>" },
                    instruction_template = "ChatML",
                    mode = "instruct",
                    top_p = 0.9,
                    min_p = 0,
                    top_k = 20,
                    num_beams = 1,
                    repetition_penalty = 1,
                    repetition_penalty_range = 1024,
                    do_sample = true,
                    frequency_penalty = 0
                };

                json = JsonConvert.SerializeObject(payload);
            }
            else
            {
                json = $"{{\"frequency_penalty\": 0.2, \"n_predict\": 1000, \"prompt\": \"<reserved_106>将下面的日文文本翻译成中文：{line}<reserved_107>\", \"repeat_penalty\": 1, \"temperature\": 0.1, \"top_k\": 40, \"top_p\": 0.3}}";
            }
            return json;
        }
    }
}
