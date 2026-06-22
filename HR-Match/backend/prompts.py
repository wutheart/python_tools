JD_PROMPT = """\
任务
将HR写的自然语言岗位要求转为JSON。

输出 JSON 格式
{
  "skills": [{"name": "技能名", "level": "熟练程度", "years": 年限数字}],
  "education": {"level": "学历要求", "major": "专业要求"},
  "experience": {"years": 年限数字, "domain": "领域"}
}
"""

RESUME_AGENT_PROMPT = """
任务
从简历文本中提取候选人信息，输出格式为json，

规则
信息缺失时填 null 或 []，不编造信息
技能名保留原文，不要改写
项目描述保留原文关键语句

输入格式
简历文本以<resume>标签包裹。

步骤
1. 先寻找姓名和联系方式
2. 再寻找教育经历（学校、专业、学历、时间）
3. 再列技能清单（一个技能一条）
4. 再列工作经历和项目
5. 最后列证书和链接
6.项目描述中如有具体数字，标记has_data=true

输出json格式
{
    "name":null,
    "contact": {"phone": null, "email": null},
    "education": [{"school": "", "major": "", "degree": "", "year": ""}],
    "skills": [{"name": "", "years": null}],
    "experience": [{"company": "", "title": "", "years": "", "description": ""}],
    "projects": [{"name": "", "role": "", "description": "", "has_data": false}],
    "certificates": [{"name": "", "date": null}],
    "links": []
    }
"""

MATCH_AGENT_PROMPT = """\
# 任务
对比 JD 要求和候选人信息，给出匹配度评分。**必须严格使用下面的计算公式，不要主观判断。**

# 输入
<jd> JD JSON, <candidate> 候选人 JSON, <weights> 权重, <preferences> HR偏好

# ======== 硬性评分公式（必须逐条套用）========

## 一、技能分（每个 JD 要求的技能单独评分，然后取平均）
单个技能评分规则：
- 候选人简历中明确列出同名或近义词 → 100
- 候选人有同类可迁移技能 → 固定 70，不得改
  可迁移对照表（只允许以下映射）：
  Flask <-> Django <-> FastAPI
  MySQL <-> PostgreSQL
  React <-> Vue <-> Angular
  PyTorch <-> TensorFlow
  Docker <-> K8s
- JD 技能在候选人简历中完全找不到 → 0

JD技能总分 = 所有JD技能得分之和 / JD技能数量
技能维度最终分 = JD技能总分 x (候选人技能年限 / max(JD要求年限, 1))

## 二、学历分
- 学历同级 → 100
- 学历高一级 → 110
- 学历低一级 → 70
- 专业完全匹配 → 100
- 专业相关 → 80
- 专业不相关 → 60
最终学历分 = (学历匹配分 + 专业匹配分) / 2

## 三、经验分
- 候选人年限 >= JD要求年限 → 100
- 候选人年限 >= JD要求年限 x 0.6 → INT(候选人年限 / JD要求年限 x100)
- 候选人年限 < JD要求年限 x 0.6 → 50

## 四、加权总分
INT(技能分 x 技能权重% + 学历分 x 学历权重% + 经验分 x 经验权重%)

# ======== 输出 JSON ========
{
  "overall_score": 0,
  "calculation": "技能Xx50% + 学历Yx20% + 经验Zx30% = 总分",
  "dimensions": {
    "skills": {"score": 0, "matched": [], "partial": [], "missing": [], "reason": ""},
    "education": {"score": 0, "reason": ""},
    "experience": {"score": 0, "reason": ""}
  },
  "preferences": [{"text": "", "matched": false, "note": ""}],
  "quality_notes": [],
  "strengths": [],
  "gaps": [],
  "interview_questions": []
}"""

MATCH_FEWSHOT_EXAMPLE = """
# 示例：Python后端开发 JD x 候选人张三

<jd>
{"skills":[{"name":"Python","years":3},{"name":"Django","years":2}],"education":{"level":"本科","major":"计算机相关"},"experience":{"years":3}}
</jd>

<candidate>
{"skills":[{"name":"Python","years":2},{"name":"Flask","years":2},{"name":"MySQL","years":1}],"education":[{"degree":"本科","major":"软件工程"}],"experience":[{"years":"2年","description":"后端API开发"}],"projects":[{"name":"订单系统","description":"Flask开发，日处理1000单","has_data":true}]}
</candidate>

<weights>{"skills":50,"education":20,"experience":30}</weights>
<preferences>希望有开源贡献经验</preferences>

## 计算过程
- Python: 同名 → 100
- Django: Flask<->Django → 70
- JD技能平均：(100+70)/2 = 85
- 技能年限调整：85 x (2/3) = 57
- 学历：同级100 + 专业匹配100 = 200/2 = 100
- 经验：2年/3年 = 67%（>=60%阈值所以用公式）
- 总分：INT(57x0.5 + 100x0.2 + 67x0.3) = INT(28.5+20+20.1) = 69

## 正确输出 JSON
{
  "overall_score": 69,
  "calculation": "技能57x50% + 学历100x20% + 经验67x30% = 69",
  "dimensions": {
    "skills": {"score":57,"matched":[{"name":"Python","match":100}],"partial":[{"name":"Django","match":70,"note":"Flask与Django属于可迁移框架"}],"missing":[],"reason":"Python=100, Django->Flask=70, 平均85, 年限调整x0.67=57"},
    "education":{"score":100,"reason":"本科+软件工程，与计算机相关完全匹配"},
    "experience":{"score":67,"reason":"2年/3年=67%, 高于60%阈值"}
  },
  "preferences":[{"text":"开源贡献","matched":false,"note":"简历中无GitHub或开源项目提及"}],
  "quality_notes":["订单系统项目有量化数据(日处理1000单)"],
  "strengths":["Python基础扎实","Flask经验可迁移至Django"],
  "gaps":["Django直接经验缺失","工作年限与要求差距1年"],
  "interview_questions":["如果从Flask迁移到Django，你会怎么设计？","参与过开源项目吗？"]
}
"""
