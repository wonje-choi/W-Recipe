class Safety:
    def __init__(self, core):
        self.core = core

    def to_list(self, value):
        if value in [None, ""]:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            text = value.strip()
            if text.startswith("["):
                parsed = self.core.json_loads(text, [])
                if isinstance(parsed, list):
                    return parsed
            return [item.strip() for item in text.split(",") if item.strip()]
        return []

    def unique(self, values):
        result = []
        for value in values:
            if value and value not in result:
                result.append(value)
        return result

    def add_issue(self, issues, risk_flags, issue_type, severity, message, matched=None):
        if matched is None:
            matched = []
        issues.append({
            "type": issue_type,
            "severity": severity,
            "message": message,
            "matched": self.unique(matched),
        })
        risk_flags.append(issue_type)

    def check_text(self, text, purpose="", baby_age_month=0):
        text = text or ""
        issues = []
        risk_flags = []
        allergen_keywords = ["대두", "콩", "달걀", "계란", "우유", "유제품", "밀", "땅콩", "견과", "호두", "아몬드", "새우", "게", "고등어", "조개", "오징어", "복숭아", "토마토"]
        high_sodium_keywords = ["소금", "간장", "된장", "고추장", "쌈장", "액젓", "젓갈", "장아찌", "햄", "베이컨", "소시지", "라면스프", "치즈", "다시다"]
        baby_unsuitable_keywords = ["꿀", "견과", "땅콩", "통포도", "떡", "사탕", "생당근", "생오이", "고추", "고춧가루", "소금", "설탕"]
        raw_keywords = ["날것", "생식", "회", "덜 익", "반숙", "생달걀", "생고기", "생선회"]
        choking_keywords = ["통째", "딱딱", "질식", "큰 덩어리", "동그란", "끈적"]
        medical_claim_keywords = ["치료", "완치", "예방", "질병 개선", "혈압이 낮아", "당뇨가 낫", "암에 좋", "의학적 효능", "보장"]

        allergens = [keyword for keyword in allergen_keywords if keyword in text]
        if allergens:
            self.add_issue(issues, risk_flags, "allergen_candidate", "warning", "알레르기 유발 가능 재료가 포함되어 있습니다.", allergens)

        high_sodium = [keyword for keyword in high_sodium_keywords if keyword in text]
        if high_sodium:
            self.add_issue(issues, risk_flags, "high_sodium_candidate", "warning", "나트륨이 높을 수 있는 재료가 포함되어 있습니다.", high_sodium)

        baby_context = purpose == self.core.constants.AI_PURPOSES["BABY_FOOD"] or "이유식" in text or "아기" in text or int(baby_age_month or 0) > 0
        if baby_context:
            baby_risks = [keyword for keyword in baby_unsuitable_keywords if keyword in text]
            raw_risks = [keyword for keyword in raw_keywords if keyword in text]
            choking_risks = [keyword for keyword in choking_keywords if keyword in text]
            if baby_risks:
                self.add_issue(issues, risk_flags, "baby_food_unsuitable", "danger", "이유식에 부적합하거나 제한이 필요한 재료가 포함되어 있습니다.", baby_risks)
            if raw_risks:
                self.add_issue(issues, risk_flags, "raw_food_risk", "danger", "영유아에게 생식 또는 덜 익은 재료는 위험할 수 있습니다.", raw_risks)
            if choking_risks:
                self.add_issue(issues, risk_flags, "choking_risk", "danger", "질식 위험이 있는 식감이나 형태가 언급되어 있습니다.", choking_risks)

        medical_claims = [keyword for keyword in medical_claim_keywords if keyword in text]
        if medical_claims:
            self.add_issue(issues, risk_flags, "medical_claim", "danger", "질병 치료, 예방, 개선 보장처럼 보일 수 있는 표현이 포함되어 있습니다.", medical_claims)

        risk_flags = self.unique(risk_flags)
        return {
            "hasRisk": len(risk_flags) > 0,
            "riskFlags": risk_flags,
            "issues": issues,
            "summary": "위험 요소 확인 필요" if risk_flags else "특이 위험 후보 없음",
        }

    def version_text(self, version):
        values = [
            version.get("title", ""),
            version.get("summary", ""),
            " ".join(self.to_list(version.get("ingredients"))),
            " ".join(self.to_list(version.get("steps"))),
            " ".join(self.to_list(version.get("cooking_tips"))),
            " ".join(self.to_list(version.get("failure_prevention_tips"))),
            " ".join(self.to_list(version.get("substitution_tips"))),
            " ".join(self.to_list(version.get("allergen_info"))),
        ]
        return " ".join([value for value in values if value])

    def modification_text(self, item):
        values = [
            item.get("purpose", ""),
            item.get("target_user_type", ""),
            item.get("original_summary", ""),
            " ".join(self.to_list(item.get("modified_ingredients"))),
            " ".join(self.to_list(item.get("modified_steps"))),
            item.get("improvement_reason", ""),
            item.get("taste_improvement_point", ""),
            item.get("sodium_reduction_point", ""),
            item.get("baby_food_safety_notes", ""),
            " ".join(self.to_list(item.get("allergen_warnings"))),
            " ".join(self.to_list(item.get("caution_notes"))),
        ]
        return " ".join([value for value in values if value])

    def check_version(self, version):
        return self.check_text(self.version_text(version))

    def check_modification(self, item):
        safety = self.check_text(self.modification_text(item), purpose=item.get("purpose", ""))
        existing_flags = self.to_list(item.get("risk_flags"))
        if existing_flags:
            safety["riskFlags"] = self.unique(safety.get("riskFlags", []) + existing_flags)
            safety["hasRisk"] = len(safety["riskFlags"]) > 0
            if safety["summary"] == "특이 위험 후보 없음":
                safety["summary"] = "위험 요소 확인 필요"
        return safety

Model = Safety
