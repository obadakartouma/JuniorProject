import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Editor from '@monaco-editor/react'
import { projectsAPI } from '../services/api'
import './ProjectWork.css'

const ProjectReview = () => {
    const { id, userId } = useParams()
    const navigate = useNavigate()

    const [project, setProject] = useState(null)
    const [tasks, setTasks] = useState([])
    const [currentIndex, setCurrentIndex] = useState(0)
    const [loading, setLoading] = useState(true)

    const [studentAnswer, setStudentAnswer] = useState('')
    const [taskFeedback, setTaskFeedback] = useState('')
    const [overallStars, setOverallStars] = useState(0)
    const [overallFeedback, setOverallFeedback] = useState('')

    useEffect(() => {
        fetchReviewData()
    }, [id, currentIndex])

    const fetchReviewData = async () => {
        try {
            const projRes = await projectsAPI.get(id)
            const tasksRes = await projectsAPI.getTasks(id)
            setProject(projRes.data.project)
            setTasks(tasksRes.data || [])

            const subRes = await projectsAPI.getSingleSubmission(id, userId);
            if (subRes.data) {
                setOverallStars(subRes.data.grade_stars || 0);
                setOverallFeedback(subRes.data.feedback || '');
            }

            const currentTask = tasksRes.data[currentIndex]
            const submissionRes = await projectsAPI.getStudentTaskSubmission(currentTask.id, userId)
            setStudentAnswer(submissionRes.data.answer || '')
            setTaskFeedback(submissionRes.data.admin_feedback || '')

            setLoading(false)
        } catch (err) {
            console.error(err)
            setLoading(false)
        }
    }

    const saveTaskFeedback = async () => {
        try {
            await projectsAPI.saveTaskFeedback(tasks[currentIndex].id, userId, {
                feedback: taskFeedback
            })
        } catch (err) { alert('خطأ في حفظ ملاحظات المهمة') }
    }

    const handleNext = async () => {
        await saveTaskFeedback()
        setCurrentIndex(prev => prev + 1)
    }

    const submitFinalReview = async () => {
        try {
            await saveTaskFeedback()
            await projectsAPI.submitFinalGrade(id, userId, {
                stars: overallStars,
                feedback: overallFeedback
            })
            alert('تم تقييم المشروع بنجاح!')
            navigate(`/projects/${id}`)
        } catch (err) { alert('خطأ في إرسال التقييم النهائي') }
    }

    if (loading) return <div className="loading">Loading Submission...</div>

    const currentTask = tasks[currentIndex]
    const isLastTask = currentIndex === tasks.length - 1

    return (
        <div className="workspace">
            {/* SIDEBAR */}
            <div className="sidebar">
                <h3>تقييم: {project.title}</h3>
                <ul>
                    {tasks.map((t, i) => (
                        <li key={t.id} className={i === currentIndex ? 'active' : ''}>
                            {t.title}
                        </li>
                    ))}
                </ul>
            </div>

            <div className="workmain">
                <div className="task-header">
                    <h2>{currentTask?.title}</h2>
                    <span>مهمة {currentIndex + 1} من {tasks.length}</span>
                </div>

                <div className="task-body">
                    <h4>إجابة الطالب:</h4>
                    {currentTask?.task_type === 'code' ? (
                        <Editor
                            height="300px"
                            language={project.language}
                            value={studentAnswer}
                            theme="vs-dark"
                            options={{ readOnly: true, minimap: { enabled: false } }}
                        />
                    ) : (
                        <div className="student-text-box">{studentAnswer}</div>
                    )}

                    <div className="admin-feedback-section">
                        <h4>ملاحظاتك على هذه المهمة:</h4>
                        <textarea
                            className="text-input"
                            value={taskFeedback}
                            onChange={(e) => setTaskFeedback(e.target.value)}
                            placeholder="اكتب ملاحظاتك للمدرب هنا..."
                        />
                    </div>
                </div>

                {/* FINAL SECTION */}
                {isLastTask && (
                    <div className="final-review-card card">
                        <h3>التقييم النهائي للمشروع</h3>
                        <div className="star-rating">
                            {[1, 2, 3, 4, 5].map(star => (
                                <span
                                    key={star}
                                    className={`star ${overallStars >= star ? 'filled' : ''}`}
                                    onClick={() => setOverallStars(star)}
                                >
                                    ★
                                </span>
                            ))}
                        </div>
                        <textarea
                            className="text-input"
                            value={overallFeedback}
                            onChange={(e) => setOverallFeedback(e.target.value)}
                            placeholder="الملاحظات النهائية على المشروع ككل..."
                        />
                    </div>
                )}

                <div className="quiz-actions">
                    <button className="btn btn-secondary" onClick={() => setCurrentIndex(c => c - 1)} disabled={currentIndex === 0}>السابق</button>
                    {isLastTask ? (
                        <button className="btn btn-success" onClick={submitFinalReview}>إنهاء التقييم</button>
                    ) : (
                        <button className="btn btn-primary" onClick={handleNext}>حفظ ومتابعة</button>
                    )}
                </div>
            </div>
        </div>
    )
}

export default ProjectReview