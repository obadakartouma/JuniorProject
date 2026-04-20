import React, { useEffect, useRef, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import Editor from '@monaco-editor/react'
import { projectsAPI } from '../services/api'
import './ProjectWork.css'

const ProjectWork = () => {
    const { id } = useParams()
    const navigate = useNavigate()

    const [project, setProject] = useState(null)
    const [tasks, setTasks] = useState([])
    const [currentIndex, setCurrentIndex] = useState(0)

    const [code, setCode] = useState('')
    const [textAnswer, setTextAnswer] = useState('')
    const [showHint, setShowHint] = useState(false)

    const [loading, setLoading] = useState(true)
    const [output, setOutput] = useState('')
    const [running, setRunning] = useState(false)
    const [lastSaved, setLastSaved] = useState({ code: '', text: '' })
    const [saving, setSaving] = useState(false)

    const codeRef = useRef('')
    const textRef = useRef('')

    const isLastTask = currentIndex === tasks.length - 1

    useEffect(() => {
        fetchData()
    }, [id])

    useEffect(() => {
        if (!tasks.length) return

        const interval = setInterval(() => {
            const currentTask = tasks[currentIndex]
            if (currentTask) {
                saveTask(false)
            }
        }, 5000)

        return () => clearInterval(interval)
    }, [tasks, currentIndex])

    useEffect(() => {
        if (!tasks.length) return
        const task = tasks[currentIndex]

        const loadSubmission = async () => {
            try {
                const res = await projectsAPI.getTaskSubmission(task.id)
                if (task.task_type === 'code') {
                    setCode(res.data.progress.answer || '')
                } else if (task.task_type === 'text') {
                    setTextAnswer(res.data.progress.answer || '')
                }

            } catch (err) {

            }
        }

        loadSubmission()
    }, [tasks, currentIndex])

    const saveTask = async () => {
        const currentTask = tasks[currentIndex]
        if (!currentTask) return

        try {
            const value =
                currentTask.task_type === 'code'
                    ? codeRef.current
                    : textRef.current

            if (!value.trim()) return

            await projectsAPI.saveTaskSubmission(currentTask.id, {
                answer: value
            })
        } catch (err) {
            console.error('Autosave error:', err)
        }
    }

    const runCode = async () => {
        setRunning(true)
        try {
            const res = await projectsAPI.executeCode(code, project.language)

            setOutput(
                res.data.stdout || res.data.stderr || 'No output'
            )
        } catch (err) {
            setOutput('Error running code')
        } finally {
            setRunning(false)
        }
    }

    const fetchData = async () => {
        try {
            const res = await projectsAPI.getTasks(id)
            const proj_res = await projectsAPI.get(id)

            const p = proj_res.data.project
            setProject(p)
            setTasks(res.data || [])

            setLoading(false)
        } catch (err) {
            console.error(err)
            setLoading(false)
        }
    }

    const task = tasks[currentIndex]

    const isTaskCompleted = () => {
        if (!task) return false

        if (task.task_type === 'code') {
            return code.trim().length > 0
        }

        if (task.task_type === 'text') {
            return textAnswer.trim().length > 0
        }

        return false
    }

    const handlePrev = () => {
        setCode('')
        setTextAnswer('')
        setShowHint(false)

        setCurrentIndex((prev) => Math.max(prev - 1, 0))
    }

    const handleNext = async () => {
        if (!isTaskCompleted()) return

        await saveTask()

        setCode('')
        setTextAnswer('')
        setShowHint(false)

        setCurrentIndex((prev) => Math.min(prev + 1, tasks.length - 1))
    }

    const handleFinish = async () => {
        if (!isTaskCompleted()) return

        try {
            await saveTask()
            await projectsAPI.complete(id)
            alert('🎉 تم إكمال المشروع بنجاح!')
            navigate('/projects')
        } catch (err) {
            console.error('Error completing project:', err)
            alert('حدث خطأ أثناء الحفظ.')
        }
    }

    const progressPercentage = tasks.length > 0
        ? Math.round(((currentIndex + 1) / tasks.length) * 100)
        : 0;

    if (loading) return <div className="loading">Loading...</div>
    if (!project) return <div>Project not found</div>

    return (
        <div className="workspace">

            {/* SIDEBAR */}
            <div className="sidebar">
                <h3>{project.title}</h3>

                <ul>
                    {tasks.map((t, i) => (
                        <li
                            key={t.id}
                            className={i === currentIndex ? 'active' : ''}
                        >
                            {t.title}
                        </li>
                    ))}
                </ul>
            </div>

            {/* MAIN */}
            <div className="main">

                <div className="progress-container">
                    <div className="progress-label">
                        <span>نسبة الإنجاز</span>
                        <span>{progressPercentage}%</span>
                    </div>
                    <div className="progress-bar-bg">
                        <div
                            className="progress-bar-fill"
                            style={{ width: `${progressPercentage}%` }}
                        ></div>
                    </div>
                </div>

                <div className="task-header">
                    <h2>{task?.title}</h2>
                    <span>{currentIndex + 1} / {tasks.length}</span>
                </div>

                <div className="quiz-question">
                    <h3>{task?.description}</h3>
                </div>

                <div className="task-body">
                    {task?.task_type === 'code' && (
                        <div className="code-editor-container">
                            <div className="monaco-wrapper">
                                <Editor
                                    height="400px"
                                    language={project.language || "javascript"}
                                    value={code}
                                    onChange={(v) => {
                                        codeRef.current = v || ''
                                        setCode(v || '')
                                    }}
                                    theme="vs-dark"
                                    options={{
                                        minimap: { enabled: false },
                                        fontSize: 14,
                                        automaticLayout: true,
                                        renderWhitespace: "all",
                                        colorDecorators: true,
                                        fixedOverflowWidgets: true,
                                        suggestWidgetFixed: true
                                    }}
                                />
                            </div>

                            <div className="editor-actions">
                                <button className="btn btn-success" onClick={runCode} disabled={running}>
                                    {running ? '⏳ Running...' : '▶ تشغيل الكود'}
                                </button>
                            </div>

                            {output && (
                                <div className="output-section">
                                    <small style={{ color: 'var(--text-secondary)', marginBottom: '5px', display: 'block' }}>Output:</small>
                                    <pre className="output-box">{output}</pre>
                                </div>
                            )}
                        </div>
                    )}

                    {task?.task_type === 'text' && (
                        <textarea
                            className="text-input"
                            value={textAnswer}
                            onChange={(e) => {
                                textRef.current = e.target.value
                                setTextAnswer(e.target.value)
                            }}
                            placeholder="اكتب إجابتك هنا..."
                        />
                    )}

                    {/* HINT */}
                    <div className="hint-section">
                        <button
                            className="btn btn-secondary"
                            onClick={() => setShowHint(!showHint)}
                        >
                            💡 عرض التلميح
                        </button>

                        {showHint && (
                            <div className="hint-box">
                                {task?.hint}
                            </div>
                        )}
                    </div>

                </div>

                {/* ACTIONS */}
                <div className="quiz-actions">

                    <button
                        className="btn btn-secondary"
                        onClick={handlePrev}
                        disabled={currentIndex === 0}
                    >
                        السابق
                    </button>

                    {isLastTask ? (
                        <button
                            className="btn btn-success"
                            onClick={handleFinish}
                            disabled={!isTaskCompleted()}
                        >
                            تسليم المشروع
                        </button>
                    ) : (
                        <button
                            className="btn btn-primary"
                            onClick={handleNext}
                            disabled={!isTaskCompleted()}
                        >
                            التالي
                        </button>
                    )}

                </div>

            </div>
        </div>
    )
}

export default ProjectWork