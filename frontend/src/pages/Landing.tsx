import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  ChartBarIcon,
  CubeIcon,
  CloudArrowUpIcon,
  CpuChipIcon,
  DocumentChartBarIcon,
  UsersIcon,
  ArrowRightIcon,
  CheckIcon,
  SparklesIcon,
  GlobeAltIcon,
  RocketLaunchIcon,
} from '@heroicons/react/24/outline'

const features = [
  {
    name: 'AI-Powered Analysis',
    description: 'Advanced machine learning algorithms optimize drainage network design and predict flood patterns with unprecedented accuracy.',
    icon: CpuChipIcon,
  },
  {
    name: 'Interactive 3D Visualization',
    description: 'Explore your terrain models in stunning 3D with real-time rendering, annotations, and collaborative viewing.',
    icon: CubeIcon,
  },
  {
    name: 'Smart Data Processing',
    description: 'Import GeoTIFF, LAS, shapefiles, and 50+ formats. Automatic preprocessing and quality validation included.',
    icon: CloudArrowUpIcon,
  },
  {
    name: 'Real-time Analytics',
    description: 'Instant hydrological calculations including flow accumulation, watershed delineation, and network optimization.',
    icon: ChartBarIcon,
  },
  {
    name: 'Automated Reporting',
    description: 'Generate professional engineering reports with one click. Perfect for permits, clients, and stakeholders.',
    icon: DocumentChartBarIcon,
  },
  {
    name: 'Team Collaboration',
    description: 'Work together in real-time with version control, commenting, and seamless project sharing.',
    icon: UsersIcon,
  },
]

const stats = [
  { value: '10K+', label: 'Projects Completed' },
  { value: '500+', label: 'Engineering Firms' },
  { value: '99.9%', label: 'Uptime Guarantee' },
  { value: '< 5min', label: 'Analysis Time' },
]

const pricingPlans = [
  {
    name: 'Starter',
    price: 'Free',
    description: 'Perfect for learning and small projects',
    features: ['3 active projects', 'Basic analysis tools', '2D visualization', 'Community support', '100MB storage'],
    cta: 'Get Started',
    popular: false,
  },
  {
    name: 'Professional',
    price: '$99',
    period: '/month',
    description: 'For professional engineers and consultants',
    features: ['Unlimited projects', 'Full AI analysis suite', '3D visualization & export', 'Priority support', '50GB storage', 'Team collaboration', 'Custom reports'],
    cta: 'Start Free Trial',
    popular: true,
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    description: 'For large organizations with custom needs',
    features: ['Everything in Professional', 'Unlimited team members', 'On-premise deployment', 'Custom integrations', 'Dedicated support', 'SLA guarantee'],
    cta: 'Contact Sales',
    popular: false,
  },
]

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 }
}

export default function Landing() {
  return (
    <div className="min-h-screen bg-slate-950 overflow-hidden">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-slate-950/80 backdrop-blur-xl border-b border-slate-800/50">
        <div className="container-wide flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center">
              <GlobeAltIcon className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-white">Terra Pravah</span>
          </Link>
          
          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="nav-link">Features</a>
            <a href="#pricing" className="nav-link">Pricing</a>
            <a href="#about" className="nav-link">About</a>
          </div>
          
          <div className="flex items-center gap-4">
            <Link to="/login" className="btn-ghost">Sign In</Link>
            <Link to="/register" className="btn-primary">Get Started</Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-24 overflow-hidden">
        {/* Background Effects */}
        <div className="absolute inset-0 mesh-gradient" />
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-indigo-500/20 rounded-full blur-3xl opacity-30" />
        
        <div className="container-wide relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center max-w-4xl mx-auto"
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-sm font-medium mb-8"
            >
              <SparklesIcon className="w-4 h-4" />
              <span>AI-Powered Drainage Design Platform</span>
            </motion.div>

            <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
              Design Drainage Networks
              <span className="block mt-2 gradient-text">10x Faster</span>
            </h1>

            <p className="text-xl text-slate-400 mb-10 max-w-2xl mx-auto leading-relaxed">
              The industry's most advanced platform for hydrological analysis and drainage design. 
              Trusted by leading engineering firms worldwide.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link to="/register" className="btn-primary text-lg px-8 py-4 group">
                Start Free Trial
                <ArrowRightIcon className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <a href="#demo" className="btn-secondary text-lg px-8 py-4">
                Watch Demo
              </a>
            </div>

            <p className="mt-6 text-sm text-slate-500">
              No credit card required • 14-day free trial • Cancel anytime
            </p>
          </motion.div>

          {/* Dashboard Preview */}
          <motion.div
            initial={{ opacity: 0, y: 60 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.4 }}
            className="mt-20 relative"
          >
            <div className="absolute -inset-4 bg-gradient-to-r from-indigo-500/20 via-violet-500/20 to-purple-500/20 rounded-3xl blur-2xl" />
            <div className="relative rounded-2xl overflow-hidden border border-slate-800/50 bg-slate-900/50 backdrop-blur-sm shadow-2xl">
              <div className="flex items-center gap-2 px-4 py-3 bg-slate-900/80 border-b border-slate-800/50">
                <div className="w-3 h-3 rounded-full bg-rose-500" />
                <div className="w-3 h-3 rounded-full bg-amber-500" />
                <div className="w-3 h-3 rounded-full bg-emerald-500" />
                <span className="ml-4 text-xs text-slate-500">Terra Pravah Dashboard</span>
              </div>
              <img
                src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200&h=600&fit=crop"
                alt="Dashboard Preview"
                className="w-full h-auto opacity-90"
              />
            </div>
          </motion.div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 border-y border-slate-800/50 bg-slate-900/30">
        <div className="container-wide">
          <motion.div
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="grid grid-cols-2 md:grid-cols-4 gap-8"
          >
            {stats.map((stat) => (
              <motion.div key={stat.label} variants={itemVariants} className="text-center">
                <div className="text-4xl md:text-5xl font-bold gradient-text mb-2" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
                  {stat.value}
                </div>
                <div className="text-slate-500">{stat.label}</div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24" id="features">
        <div className="container-wide">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="section-title">
              Everything you need for
              <span className="gradient-text"> professional drainage design</span>
            </h2>
            <p className="section-subtitle">
              Powerful tools that help engineering teams design, analyze, and optimize drainage networks with unprecedented efficiency.
            </p>
          </motion.div>

          <motion.div
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="grid md:grid-cols-2 lg:grid-cols-3 gap-6"
          >
            {features.map((feature) => (
              <motion.div
                key={feature.name}
                variants={itemVariants}
                className="card-hover group p-6"
              >
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500/20 to-violet-500/20 border border-indigo-500/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <feature.icon className="w-6 h-6 text-indigo-400" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-indigo-400 transition-colors">
                  {feature.name}
                </h3>
                <p className="text-slate-400 text-sm leading-relaxed">{feature.description}</p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-slate-950 via-indigo-950/20 to-slate-950" />
        <div className="container-narrow relative z-10">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="relative rounded-3xl overflow-hidden"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-indigo-600/20 to-violet-600/20" />
            <div className="absolute inset-0 bg-slate-900/80 backdrop-blur-xl" />
            <div className="relative p-12 text-center">
              <RocketLaunchIcon className="w-16 h-16 text-indigo-400 mx-auto mb-6" />
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-4" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
                Ready to transform your workflow?
              </h2>
              <p className="text-slate-400 max-w-xl mx-auto mb-8">
                Join thousands of engineering professionals who are already delivering projects faster with Terra Pravah.
              </p>
              <Link to="/register" className="btn-primary text-lg px-8 py-4">
                Start Your Free Trial
                <ArrowRightIcon className="w-5 h-5" />
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-24" id="pricing">
        <div className="container-wide">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="section-title">
              Simple, <span className="gradient-text">transparent pricing</span>
            </h2>
            <p className="section-subtitle">
              Choose the plan that fits your needs. All plans include a 14-day free trial.
            </p>
          </motion.div>

          <motion.div
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto"
          >
            {pricingPlans.map((plan) => (
              <motion.div
                key={plan.name}
                variants={itemVariants}
                className={`card relative ${plan.popular ? 'border-indigo-500/50 bg-slate-900/80' : ''}`}
              >
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <span className="badge-primary">Most Popular</span>
                  </div>
                )}
                <div className="text-center mb-6 pt-2">
                  <h3 className="text-lg font-semibold text-white mb-2">{plan.name}</h3>
                  <div className="flex items-baseline justify-center gap-1">
                    <span className="text-4xl font-bold text-white" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>{plan.price}</span>
                    {plan.period && <span className="text-slate-500">{plan.period}</span>}
                  </div>
                  <p className="text-sm text-slate-500 mt-2">{plan.description}</p>
                </div>
                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-3 text-sm">
                      <CheckIcon className="w-5 h-5 text-indigo-400 flex-shrink-0 mt-0.5" />
                      <span className="text-slate-300">{feature}</span>
                    </li>
                  ))}
                </ul>
                <Link
                  to="/register"
                  className={`w-full ${plan.popular ? 'btn-primary' : 'btn-secondary'} justify-center`}
                >
                  {plan.cta}
                </Link>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-slate-800/50">
        <div className="container-wide">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center">
                <GlobeAltIcon className="w-5 h-5 text-white" />
              </div>
              <span className="text-lg font-semibold text-white">Terra Pravah</span>
            </div>
            <div className="flex items-center gap-8 text-sm text-slate-500">
              <a href="#" className="hover:text-white transition-colors">Privacy Policy</a>
              <a href="#" className="hover:text-white transition-colors">Terms of Service</a>
              <a href="#" className="hover:text-white transition-colors">Contact</a>
            </div>
            <p className="text-sm text-slate-600">
              © 2026 Terra Pravah. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
