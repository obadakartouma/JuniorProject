import React from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import './Home.css'

const Home = () => {
  const { isAuthenticated } = useAuth()

  const learningSteps = [
    {
      number: 1,
      title: 'إنشاء حسابك',
      description: 'سجل مجاناً وقم بإعداد ملفك التعليمي. اختر مستواك المهاراتي والتقنيات التي تريد تعلمها.',
      icon: '👤'
    },
    {
      number: 2,
      title: 'أجب على اختبار المهارات',
      description: 'أجب على بضعة أسئلة سريعة لتحديد مستواك الحالي. سنخصص مسارك التعليمي بناءً على نتائجك.',
      icon: '📝'
    },
    {
      number: 3,
      title: 'ابدأ مشاريع حقيقية',
      description: 'تعلم من خلال بناء مشاريع واجهة أمامية حقيقية. كل تحدي يساعدك على ممارسة HTML و CSS و JavaScript خطوة بخطوة.',
      icon: '🚀'
    },
    {
      number: 4,
      title: 'تتبع تقدمك',
      description: 'اكسب النقاط، افتح تحديات جديدة، وشاهد كيف تتحسن مهاراتك البرمجية مع مرور الوقت.',
      icon: '📊'
    }
  ]

  const whyChooseUs = [
    {
      title: 'مشاريع حقيقية',
      description: 'تعلم من خلال بناء مشاريع عملية تستخدم في العالم الحقيقي'
    },
    {
      title: 'مسار تعليمي مخصص',
      description: 'نظام ذكي يحدد مستواك ويقدم لك المحتوى المناسب'
    },
    {
      title: 'تتبع التقدم',
      description: 'راقب تقدمك وتطور مهاراتك مع إحصائيات مفصلة'
    },
    {
      title: 'مجتمع نشط',
      description: 'انضم إلى مجتمع من المتعلمين والمطورين'
    }
  ]

  const projectExamples = [
    {
      title: 'صفحة هبوط تفاعلية',
      description: 'بناء صفحة هبوط احترافية باستخدام HTML و CSS و JavaScript',
      level: 'مبتدئ',
      time: '5 ساعات'
    },
    {
      title: 'تطبيق قائمة المهام',
      description: 'تطبيق لإدارة المهام مع إمكانية الإضافة والحذف والتعديل',
      level: 'متوسط',
      time: '8 ساعات'
    },
    {
      title: 'لوحة تحكم تفاعلية',
      description: 'بناء لوحة تحكم كاملة مع الرسوم البيانية والإحصائيات',
      level: 'متقدم',
      time: '15 ساعة'
    }
  ]

  return (
    <div className="home-page">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="container">
          <div className="hero-content">
            <h1 className="hero-title">التعلم القائم على المشاريع</h1>
            <p className="hero-description">
              منصة تعليمية مبتكرة تجمع بين التعلم النظري والتطبيق العملي. 
              تعلم البرمجة من خلال بناء مشاريع حقيقية خطوة بخطوة. 
              ابدأ رحلتك التعليمية اليوم واكتسب المهارات التي تحتاجها لتصبح مطوراً محترفاً.
            </p>
            <div className="hero-actions">
              <Link to="/register" className="btn btn-primary btn-large">
                ابدأ مجاناً
              </Link>
            </div>
            
            {/* Platform Statistics */}
            <div className="platform-stats">
              <div className="stat-item">
                <div className="stat-number">1000+</div>
                <div className="stat-label">متعلم نشط</div>
              </div>
              <div className="stat-item">
                <div className="stat-number">50+</div>
                <div className="stat-label">مشروع تعليمي</div>
              </div>
              <div className="stat-item">
                <div className="stat-number">95%</div>
                <div className="stat-label">معدل النجاح</div>
              </div>
              <div className="stat-item">
                <div className="stat-number">24/7</div>
                <div className="stat-label">دعم متواصل</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Your Learning Journey */}
      <section className="learning-journey-section">
        <div className="container">
          <h2 className="section-title">رحلتك التعليمية</h2>
          <div className="steps-container">
            {learningSteps.map((step, index) => (
              <div key={step.number} className="step-card">
                <div className="step-icon">{step.icon}</div>
                <div className="step-number">{step.number}</div>
                <h3 className="step-title">{step.title}</h3>
                <p className="step-description">{step.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Why Choose Our Platform */}
      <section className="why-choose-section">
        <div className="container">
          <h2 className="section-title">لماذا تختار منصتنا؟</h2>
          <div className="features-grid">
            {whyChooseUs.map((feature, index) => (
              <div key={index} className="feature-card">
                <h3 className="feature-title">{feature.title}</h3>
                <p className="feature-description">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Project Examples */}
      <section className="project-examples-section">
        <div className="container">
          <h2 className="section-title">أمثلة المشاريع التعليمية</h2>
          <div className="projects-grid">
            {projectExamples.map((project, index) => (
              <div key={index} className="project-example-card">
                <div className="project-badge">{project.level}</div>
                <h3 className="project-title">{project.title}</h3>
                <p className="project-description">{project.description}</p>
                <div className="project-time">⏱️ {project.time}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="home-footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-brand">
              <h3>منصة التعلم</h3>
              <p>منصة التعلم القائمة على المشاريع</p>
            </div>
            <div className="footer-links">
              <div className="footer-column">
                <h4>روابط سريعة</h4>
                <Link to="/">الرئيسية</Link>
                <Link to="/courses">المسارات</Link>
                <Link to="/projects">المشاريع</Link>
              </div>
              <div className="footer-column">
                <h4>حسابي</h4>
                {isAuthenticated ? (
                  <>
                    <Link to="/dashboard">لوحة التحكم</Link>
                    <Link to="/profile">الملف الشخصي</Link>
                  </>
                ) : (
                  <>
                    <Link to="/login">تسجيل الدخول</Link>
                    <Link to="/register">إنشاء حساب</Link>
                  </>
                )}
              </div>
              <div className="footer-column">
                <h4>تواصل معنا</h4>
                <p>البريد الإلكتروني: info@buildly.com</p>
                <p>الدعم: support@buildly.com</p>
              </div>
            </div>
          </div>
          <div className="footer-bottom">
            <p>&copy; 2024 منصة التعلم. جميع الحقوق محفوظة.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Home

