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
你是资深招聘评估专家。对比 JD 要求和候选人信息，给出匹配度评分和能力评估。发挥你的语义理解能力——你不是计算器，你是能读懂简历背后含义的HR专家。

# 输入
<jd> JD JSON, <candidate> 候选人 JSON, <weights> 权重, <preferences> HR偏好

# ======== 评分规则 ========

## 技能匹配（逐个评判，发挥语义理解）
- 同名技能 → 100%
- 同类可迁移 → 70%（参考但不限于以下映射：Flask↔Django↔FastAPI, MySQL↔PostgreSQL, React↔Vue, PyTorch↔TensorFlow, Docker↔K8s。遇到映射表外的技能，用你的专业知识判断是否可迁移）
- 完全不同方向 → 0%
- 技能年限打折：候选人年限够用 → 不打折；明显不足 → 适度扣分

## 学历匹配
- 同级100 / 高一级110 / 低一级上限70
- 专业完全匹配100 / 相关80 / 不相关60

## 经验匹配
- 够用→100，基本够→按比例，差太多→上限50

## 加权
总分 = 技能分×权重 + 学历分×权重 + 经验分×权重

## 能力评估（不影响总分，发挥你的判断力）
从以下几个维度综合评价候选人的真实能力水平：
- 项目深度：描述空洞还是言之有物
- 技能自洽：技能栏和项目栏是否互相印证
- 成长潜力：技能栈广度、项目复杂度、学习轨迹
- 亮点标记：证书、奖项、开源贡献等加分项

## HR偏好（不影响总分）
匹配的标注证据，不匹配的标注原因。

# 步骤
1. 阅读候选人简历，理解其真实技术背景
2. 逐项对比JD要求，用上述规则打分
3. 综合评估候选人能力水平
4. 生成2-3个有针对性的面试追问

# 输出 JSON
{
  "overall_score": 0,
  "calculation": "技能Xx权重 + 学历Yx权重 + 经验Zx权重 = 总分",
  "dimensions": {
    "skills": {"score": 0, "matched": [], "partial": [], "missing": [], "reason": ""},
    "education": {"score": 0, "reason": ""},
    "experience": {"score": 0, "reason": ""}
  },
  "preferences": [{"text": "", "matched": false, "note": ""}],
  "capability_assessment": {"depth": "", "self_consistency": "", "growth_potential": "", "highlights": "", "summary": ""},
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
  "capability_assessment": {"depth":"项目有量化数据，日处理1000单","self_consistency":"Flask经验与项目匹配","growth_potential":"Python基础扎实，可迁移至Django","highlights":"无","summary":"技术水平扎实，经验略有不足"},

  "strengths":["Python基础扎实","Flask经验可迁移至Django"],
  "gaps":["Django直接经验缺失","工作年限与要求差距1年"],
  "interview_questions":["如果从Flask迁移到Django，你会怎么设计？","参与过开源项目吗？"]
}
"""
