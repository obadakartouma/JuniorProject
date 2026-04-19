import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import Editor from '@monaco-editor/react'
import { projectsAPI } from '../services/api'
import './ProjectWork.css'

const ProjectWork = () => {
    const { id } = useParams()

    const [project, setProject] = useState(null)
    const [tasks, setTasks] = useState([])
    const [currentIndex, setCurrentIndex] = useState(0)

    const [code, setCode] = useState('')
    const [textAnswer, setTextAnswer] = useState('')
    const [showHint, setShowHint] = useState(false)

    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchData()
    }, [id])

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

    const handleNext = () => {
        if (!isTaskCompleted()) return

        setCode('')
        setTextAnswer('')
        setShowHint(false)

        setCurrentIndex((prev) => Math.min(prev + 1, tasks.length - 1))
    }

    const handlePrev = () => {
        setCode('')
        setTextAnswer('')
        setShowHint(false)

        setCurrentIndex((prev) => Math.max(prev - 1, 0))
    }

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

                <div className="task-header">
                    <h2>{task?.title}</h2>
                    <span>{currentIndex + 1} / {tasks.length}</span>
                </div>

                <div className="quiz-question">
                    <h3>{task?.description}</h3>
                </div>

                <div className="task-body">
                    {task?.task_type === 'code' && (
                        <div style={{ height: '400px', width: '100%', direction: 'ltr' }}>
                            <Editor
                                height="400px"
                                language="javascript"
                                value={code}
                                onChange={(v) => setCode(v || '')}
                                theme="vs"
                                options={{
                                    minimap: { enabled: false },
                                    fontSize: 14,
                                    automaticLayout: true,
                                    renderWhitespace: "all",
                                    colorDecorators: true,
                                }}
                            />
                        </div>
                    )}

                    {task?.task_type === 'text' && (
                        <textarea
                            className="text-input"
                            value={textAnswer}
                            onChange={(e) => setTextAnswer(e.target.value)}
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

                    <button
                        className="btn btn-primary"
                        onClick={handleNext}
                        disabled={!isTaskCompleted()}
                    >
                        التالي
                    </button>

                </div>

            </div>
        </div>
    )
}

export default ProjectWork