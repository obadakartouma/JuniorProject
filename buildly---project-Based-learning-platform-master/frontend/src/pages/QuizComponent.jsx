import React, { useState } from "react"
import "./Quiz.css"

const QuizComponent = ({ onFinish }) => {
  const [current, setCurrent] = useState(0)
  const [answers, setAnswers] = useState({})

  const questions = [
    {
      q: "ما دور HTML في الويب؟",
      options: ["تنسيق الواجهة", "هيكلة الصفحة", "إدارة قاعدة البيانات", "تشغيل السيرفر"],
      correct: 1
    },
    {
      q: "أي عنصر يُستخدم لربط ملف CSS؟",
      options: ["<style>", "<script>", "<link>", "<meta>"],
      correct: 2
    },
    {
      q: "ما هو الهدف من JavaScript في الواجهة؟",
      options: ["إضافة التفاعل", "تعريف الجداول", "رفع الصور فقط", "تشغيل DNS"],
      correct: 0
    },
    {
      q: "ما أفضل مكان لنداء API في React غالبا؟",
      options: ["داخل JSX مباشرة", "داخل useEffect", "داخل CSS", "داخل HTML"],
      correct: 1
    },
    {
      q: "ما معنى REST API؟",
      options: ["أسلوب للتواصل بين العميل والخادم", "تنسيق خط", "قاعدة بيانات", "محرر أكواد"],
      correct: 0
    },
    {
      q: "أي HTTP method يستخدم غالبا لإنشاء مورد؟",
      options: ["GET", "POST", "PUT", "DELETE"],
      correct: 1
    },
    {
      q: "ما وظيفة useState في React؟",
      options: ["إدارة الحالة", "التنقل بين الصفحات", "إنشاء API", "حفظ الصور"],
      correct: 0
    },
    {
      q: "ما الفرق الأساسي بين GET و POST؟",
      options: ["لا يوجد فرق", "GET للقراءة وPOST للإرسال/الإنشاء", "POST أسرع دائما", "GET محظور"],
      correct: 1
    },
    {
      q: "في Django، ما دور Serializer؟",
      options: ["تحويل البيانات والتحقق منها", "تصميم CSS", "تشغيل الخادم", "كتابة SQL فقط"],
      correct: 0
    },
    {
      q: "ما الفائدة من تقسيم المشروع إلى Frontend و Backend؟",
      options: ["زيادة التعقيد فقط", "فصل المسؤوليات وسهولة الصيانة", "لا فائدة", "استبدال قاعدة البيانات"],
      correct: 1
    }
  ]

  const handleSelect = (index) => {
    setAnswers({ ...answers, [current]: index })
  }

  const next = () => {
    if (current < questions.length - 1) {
      setCurrent(current + 1)
    }
  }

  const prev = () => {
    if (current > 0) {
      setCurrent(current - 1)
    }
  }

  const finish = () => {
    let score = 0;

    questions.forEach((q, index) => {
      if (answers[index] === q.correct) {
        score++;
      }
    });

    let level = "beginner";
    if (score >= 8) level = "advanced";
    else if (score >= 5) level = "intermediate";

    onFinish(level);
  };

  const q = questions[current]

  return (
    <div className="quiz-container">
      <div className="quiz-card">

        <div className="quiz-header">
          <h2>تحديد المستوى</h2>
          <span>{current + 1} / {questions.length}</span>
        </div>

        <h3 className="quiz-question">{q.q}</h3>

        <div className="quiz-options">
          {q.options.map((opt, i) => (
            <button
              key={i}
              className={`quiz-option ${answers[current] === i ? "selected" : ""}`}
              onClick={() => handleSelect(i)}
            >
              {opt}
            </button>
          ))}
        </div>

        <div className="quiz-actions">
          <button
            onClick={prev}
            disabled={current === 0}
            className="btn btn-secondary"
          >
            رجوع
          </button>

          {current < questions.length - 1 ? (
            <button
              onClick={next}
              disabled={answers[current] === undefined}
              className="btn btn-primary"
            >
              التالي
            </button>
          ) : (
            <button
              onClick={finish}
              disabled={answers[current] === undefined}
              className="btn btn-primary"
            >
              إنهاء الاختبار
            </button>
          )}
        </div>

      </div>
    </div>
  )
}

export default QuizComponent