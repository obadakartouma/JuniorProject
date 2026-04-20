import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { projectsAPI } from '../services/api'
import './Form.css'

const ProjectEdit = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    requirements: '',
    objectives: '',
    resources: '',
    estimated_time: '',
    level: 'beginner',
    language: 'python',
    order: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [fetching, setFetching] = useState(true)
  const [tasks, setTasks] = useState([])
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    task_type: 'text',
    expected_answer: '',
    hint: '',
    teaching: '',
  });

  useEffect(() => {
    fetchProject()
  }, [id])

  const fetchProject = async () => {
    try {
      setFetching(true)
      const response = await projectsAPI.get(id)
      const project = response.data.project
      setFormData({
        title: project.title,
        description: project.description,
        requirements: project.requirements || '',
        objectives: project.objectives || '',
        resources: project.resources || '',
        estimated_time: project.estimated_time,
        level: project.level,
        language: project.language,
        order: project.order || '',
      })

      const tasksResponse = await projectsAPI.getTasks(id)
      setTasks(tasksResponse.data || [])
    } catch (err) {
      setError('فشل تحميل بيانات المشروع')
    } finally {
      setFetching(false)
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData({
      ...formData,
      [name]: value,
    })
    setError('')
  }

  const handleAddTask = async () => {
    try {
      const taskToSave = {
        ...newTask,
        project: id,
        order: tasks.length + 1,
      };

      await projectsAPI.createTask(taskToSave);

      const tasksResponse = await projectsAPI.getTasks(id);
      setTasks(tasksResponse.data || []);

      setNewTask({
        title: '',
        description: '',
        task_type: 'text',
        expected_answer: '',
        hint: '',
        teaching: '',
      });
      setShowTaskModal(false);
    } catch (err) {
      console.error("Error creating task:", err);
      alert('حدث خطأ أثناء إضافة المهمة');
    }
  };

  const handleRemoveTask = async (taskId) => {
    if (!window.confirm('هل أنت متأكد من حذف هذه المهمة؟')) return

    try {
      await projectsAPI.deleteTask(taskId)
      setTasks(tasks.filter(t => t.id !== taskId))
    } catch (err) {
      alert('فشل حذف المهمة')
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const submitData = {
        ...formData,
        estimated_time: parseInt(formData.estimated_time),
        order: formData.order ? parseInt(formData.order) : undefined,
      }
      await projectsAPI.update(id, submitData)
      navigate(`/projects/${id}`)
    } catch (err) {
      const errorData = err.response?.data
      console.error('Error updating project:', err.response?.data || err.message)

      if (errorData?.message) {
        setError(errorData.message)
      } else if (errorData?.errors) {
        // معالجة أخطاء الحقول
        if (typeof errorData.errors === 'object' && !Array.isArray(errorData.errors)) {
          const fieldErrors = Object.entries(errorData.errors)
            .map(([field, messages]) => {
              const fieldName = field === 'non_field_errors' ? '' : `${field}: `
              return Array.isArray(messages)
                ? `${fieldName}${messages.join(', ')}`
                : `${fieldName}${messages}`
            })
            .join('\n')
          setError(fieldErrors || 'حدث خطأ أثناء تحديث المشروع')
        } else {
          setError(Array.isArray(errorData.errors) ? errorData.errors.join(', ') : errorData.errors)
        }
      } else if (errorData?.detail) {
        setError(errorData.detail)
      } else {
        setError(err.message || 'حدث خطأ أثناء تحديث المشروع')
      }
    } finally {
      setLoading(false)
    }
  }

  if (fetching) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    )
  }

  return (
    <div className="container">
      <div className="page-header">
        <h1>تعديل المشروع</h1>
      </div>

      <div className="form-container">
        {error && <div className="alert alert-error">{error}</div>}

        <form onSubmit={handleSubmit} className="form">
          <div className="input-group">
            <label htmlFor="title">عنوان المشروع *</label>
            <input
              type="text"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              required
              minLength={3}
              placeholder="أدخل عنوان المشروع"
            />
          </div>

          <div className="input-group">
            <label htmlFor="description">وصف المشروع *</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              required
              minLength={20}
              placeholder="أدخل وصفاً مفصلاً للمشروع"
            />
          </div>

          <div className="input-group">
            <label htmlFor="requirements">المتطلبات</label>
            <textarea
              id="requirements"
              name="requirements"
              value={formData.requirements}
              onChange={handleChange}
              placeholder="متطلبات إنجاز المشروع"
            />
          </div>

          <div className="input-group">
            <label htmlFor="objectives">الأهداف التعليمية</label>
            <textarea
              id="objectives"
              name="objectives"
              value={formData.objectives}
              onChange={handleChange}
              placeholder="الأهداف التي سيحققها الطالب"
            />
          </div>

          <div className="input-group">
            <label htmlFor="resources">الموارد</label>
            <textarea
              id="resources"
              name="resources"
              value={formData.resources}
              onChange={handleChange}
              placeholder="الموارد والمراجع المطلوبة"
            />
          </div>

          <div className="form-row">
            <div className="input-group">
              <label htmlFor="level">المستوى *</label>
              <select
                id="level"
                name="level"
                value={formData.level}
                onChange={handleChange}
                required
              >
                <option value="beginner">مبتدئ</option>
                <option value="intermediate">متوسط</option>
                <option value="advanced">متقدم</option>
                <option value="expert">خبير</option>
              </select>
            </div>

            <div className="input-group">
              <label htmlFor="language">لغة البرمجة *</label>
              <select
                id="language"
                name="language"
                value={formData.language}
                onChange={handleChange}
                required
              >
                <option value="python">Python</option>
                <option value="javascript">JavaScript</option>
                <option value="java">Java</option>
                <option value="csharp">C#</option>
                <option value="cpp">C++</option>
                <option value="php">PHP</option>
                <option value="ruby">Ruby</option>
                <option value="go">Go</option>
                <option value="swift">Swift</option>
                <option value="kotlin">Kotlin</option>
                <option value="typescript">TypeScript</option>
                <option value="dart">Dart</option>
                <option value="rust">Rust</option>
                <option value="other">أخرى</option>
              </select>
            </div>
          </div>

          <div className="tasks-section">
            <div className="tasks-header">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setShowTaskModal(true)}
              >
                ➕ إضافة مهمة جديدة
              </button>
            </div>

            <div className="tasks-section">
              <h2>مهام المشروع (Tasks)</h2>
              <div className="tasks-list">
                {tasks.length === 0 && <p>لا يوجد مهام حالياً</p>}
                {tasks.map((task, index) => (
                  <div key={task.id} className="task-card">
                    <div className="task-header">
                      <strong>{index + 1}. {task.title}</strong>
                      <button
                        type="button"
                        onClick={() => handleRemoveTask(task.id)} // Nutze die Datenbank-ID
                        className="btn btn-danger btn-sm"
                      >
                        حذف
                      </button>
                    </div>

                    <p>{task.description}</p>

                    <div className="task-meta">
                      <span>نوع المهمة: {task.task_type}</span>
                      <span style={{ marginRight: '15px' }}>الترتيب: {task.order}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>


            {showTaskModal && (
              <div className="modal-overlay">
                <div className="modal">

                  <h3>إضافة مهمة جديدة</h3>

                  <input
                    type="text"
                    placeholder="عنوان المهمة"
                    value={newTask.title}
                    onChange={(e) =>
                      setNewTask({ ...newTask, title: e.target.value })
                    }
                  />

                  <textarea
                    placeholder="وصف المهمة"
                    value={newTask.description}
                    onChange={(e) =>
                      setNewTask({ ...newTask, description: e.target.value })
                    }
                  />

                  <select
                    value={newTask.task_type}
                    onChange={(e) =>
                      setNewTask({ ...newTask, task_type: e.target.value })
                    }
                  >
                    <option value="text">نص</option>
                    <option value="code">كود</option>
                    <option value="file">ملف</option>
                  </select>

                  <textarea
                    placeholder="الإجابة المتوقعة"
                    value={newTask.expected_answer}
                    onChange={(e) =>
                      setNewTask({ ...newTask, expected_answer: e.target.value })
                    }
                  />

                  <textarea
                    placeholder="تلميح"
                    value={newTask.hint}
                    onChange={(e) =>
                      setNewTask({ ...newTask, hint: e.target.value })
                    }
                  />

                  <textarea
                    placeholder="شرح / teaching"
                    value={newTask.teaching}
                    onChange={(e) =>
                      setNewTask({ ...newTask, teaching: e.target.value })
                    }
                  />

                  <div className="modal-actions">
                    <button type="button" onClick={handleAddTask} className="btn btn-primary">
                      حفظ
                    </button>
                    <button
                      type="button"
                      onClick={() => setShowTaskModal(false)}
                      className="btn btn-secondary"
                    >
                      إلغاء
                    </button>
                  </div>

                </div>
              </div>
            )}
          </div>

          <div className="form-row">
            <div className="input-group">
              <label htmlFor="estimated_time">الوقت المقدر (بالساعات) *</label>
              <input
                type="number"
                id="estimated_time"
                name="estimated_time"
                value={formData.estimated_time}
                onChange={handleChange}
                required
                min="1"
                max="500"
                placeholder="أدخل الوقت المقدر"
              />
            </div>

            <div className="input-group">
              <label htmlFor="order">الترتيب</label>
              <input
                type="number"
                id="order"
                name="order"
                value={formData.order}
                onChange={handleChange}
                min="0"
                placeholder="ترتيب المشروع في المسار"
              />
            </div>
          </div>

          <div className="form-actions">
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'جاري التحديث...' : 'حفظ التغييرات'}
            </button>
            <button
              type="button"
              onClick={() => navigate(`/projects/${id}`)}
              className="btn btn-secondary"
            >
              إلغاء
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default ProjectEdit

