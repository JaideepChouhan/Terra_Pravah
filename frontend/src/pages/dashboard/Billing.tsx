import { useState, useEffect } from 'react'
import { 
  CreditCard, 
  Check, 
  Zap, 
  Building2, 
  Rocket,
  FileText,
  Download,
  Loader2,
  AlertTriangle,
  X,
  Crown
} from 'lucide-react'
import { billingApi } from '../../services/api'

interface Plan {
  id: string
  name: string
  price: number
  period: 'monthly' | 'yearly'
  features: string[]
  limits: {
    projects: number
    storage_gb: number
    team_members: number
  }
  popular?: boolean
}

interface Subscription {
  plan: string
  status: 'active' | 'cancelled' | 'past_due'
  current_period_end: string
  cancel_at_period_end: boolean
}

interface Invoice {
  id: string
  amount: number
  status: 'paid' | 'pending' | 'failed'
  date: string
  pdf_url?: string
}

const plans: Plan[] = [
  {
    id: 'free',
    name: 'Free',
    price: 0,
    period: 'monthly',
    features: [
      '3 projects',
      '100 MB storage',
      'Basic analysis',
      'Community support'
    ],
    limits: {
      projects: 3,
      storage_gb: 0.1,
      team_members: 1
    }
  },
  {
    id: 'professional',
    name: 'Professional',
    price: 2999,
    period: 'monthly',
    features: [
      '25 projects',
      '10 GB storage',
      'Advanced analysis',
      'D∞ flow algorithm',
      'Priority support',
      'API access',
      'Export to CAD'
    ],
    limits: {
      projects: 25,
      storage_gb: 10,
      team_members: 5
    },
    popular: true
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price: 9999,
    period: 'monthly',
    features: [
      'Unlimited projects',
      '100 GB storage',
      'All Professional features',
      'Custom integrations',
      'Dedicated support',
      'SLA guarantee',
      'On-premise option',
      'White-labeling'
    ],
    limits: {
      projects: -1,
      storage_gb: 100,
      team_members: -1
    }
  }
]

export default function Billing() {
  const [subscription, setSubscription] = useState<Subscription | null>(null)
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [loading, setLoading] = useState(true)
  const [subscribing, setSubscribing] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  useEffect(() => {
    fetchBillingData()
  }, [])

  const fetchBillingData = async () => {
    try {
      setLoading(true)
      const [subResponse, invoiceResponse] = await Promise.all([
        billingApi.getSubscription().catch(() => ({ data: { subscription: null } })),
        billingApi.getInvoices().catch(() => ({ data: { invoices: [] } }))
      ])
      setSubscription(subResponse.data.subscription)
      setInvoices(invoiceResponse.data.invoices || [])
    } catch (err) {
      console.error('Failed to fetch billing data:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSubscribe = async (planId: string) => {
    try {
      setSubscribing(planId)
      setError(null)
      await billingApi.subscribe(planId)
      setSuccess('Subscription updated successfully!')
      setTimeout(() => setSuccess(null), 3000)
      fetchBillingData()
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to update subscription')
    } finally {
      setSubscribing(null)
    }
  }

  const handleCancel = async () => {
    if (!confirm('Are you sure you want to cancel your subscription?')) return

    try {
      await billingApi.cancelSubscription()
      setSuccess('Subscription cancelled. You will have access until the end of your billing period.')
      setTimeout(() => setSuccess(null), 5000)
      fetchBillingData()
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to cancel subscription')
    }
  }

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0
    }).format(price)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  const getPlanIcon = (planId: string) => {
    switch (planId) {
      case 'free': return Zap
      case 'professional': return Building2
      case 'enterprise': return Rocket
      default: return Zap
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
      </div>
    )
  }

  const currentPlan = subscription?.plan || 'free'

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-3">
          <CreditCard className="w-7 h-7 text-primary-500" />
          Billing & Subscription
        </h1>
        <p className="text-dark-400 mt-1">
          Manage your subscription and billing information
        </p>
      </div>

      {/* Alerts */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-red-400 shrink-0" />
          <p className="text-red-400">{error}</p>
          <button onClick={() => setError(null)} className="ml-auto text-red-400 hover:text-red-300">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {success && (
        <div className="bg-primary-500/10 border border-primary-500/20 rounded-lg p-4 flex items-center gap-3">
          <Check className="w-5 h-5 text-primary-400" />
          <p className="text-primary-400">{success}</p>
        </div>
      )}

      {/* Current Subscription */}
      {subscription && (
        <div className="glass-card p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-white">Current Plan</h2>
              <div className="flex items-center gap-2 mt-2">
                <Crown className="w-5 h-5 text-primary-400" />
                <span className="text-xl font-bold text-primary-400 capitalize">
                  {subscription.plan}
                </span>
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                  subscription.status === 'active' 
                    ? 'bg-primary-500/20 text-primary-400'
                    : subscription.status === 'cancelled'
                    ? 'bg-amber-500/20 text-amber-400'
                    : 'bg-red-500/20 text-red-400'
                }`}>
                  {subscription.status}
                </span>
              </div>
              {subscription.current_period_end && (
                <p className="text-dark-400 text-sm mt-2">
                  {subscription.cancel_at_period_end 
                    ? `Expires on ${formatDate(subscription.current_period_end)}`
                    : `Renews on ${formatDate(subscription.current_period_end)}`
                  }
                </p>
              )}
            </div>
            {subscription.plan !== 'free' && subscription.status === 'active' && (
              <button
                onClick={handleCancel}
                className="btn-secondary text-red-400 border-red-500/20 hover:bg-red-500/10"
              >
                Cancel Subscription
              </button>
            )}
          </div>
        </div>
      )}

      {/* Plans */}
      <div>
        <h2 className="text-lg font-semibold text-white mb-4">Available Plans</h2>
        <div className="grid md:grid-cols-3 gap-6">
          {plans.map((plan) => {
            const Icon = getPlanIcon(plan.id)
            const isCurrentPlan = currentPlan === plan.id
            
            return (
              <div
                key={plan.id}
                className={`glass-card p-6 relative ${
                  plan.popular ? 'border-primary-500' : ''
                } ${isCurrentPlan ? 'ring-2 ring-primary-500' : ''}`}
              >
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <span className="px-3 py-1 bg-primary-500 text-white text-xs font-medium rounded-full">
                      Most Popular
                    </span>
                  </div>
                )}

                <div className="text-center mb-6">
                  <div className="w-12 h-12 mx-auto bg-dark-700 rounded-xl flex items-center justify-center mb-4">
                    <Icon className="w-6 h-6 text-primary-400" />
                  </div>
                  <h3 className="text-xl font-bold text-white">{plan.name}</h3>
                  <div className="mt-2">
                    <span className="text-3xl font-bold text-white">
                      {plan.price === 0 ? 'Free' : formatPrice(plan.price)}
                    </span>
                    {plan.price > 0 && (
                      <span className="text-dark-400">/month</span>
                    )}
                  </div>
                </div>

                <ul className="space-y-3 mb-6">
                  {plan.features.map((feature, idx) => (
                    <li key={idx} className="flex items-center gap-2 text-dark-300">
                      <Check className="w-4 h-4 text-primary-400 shrink-0" />
                      {feature}
                    </li>
                  ))}
                </ul>

                <button
                  onClick={() => !isCurrentPlan && handleSubscribe(plan.id)}
                  disabled={isCurrentPlan || subscribing === plan.id}
                  className={`w-full py-2 rounded-lg font-medium transition-all ${
                    isCurrentPlan
                      ? 'bg-dark-700 text-dark-400 cursor-not-allowed'
                      : plan.popular
                      ? 'btn-primary'
                      : 'btn-secondary'
                  }`}
                >
                  {subscribing === plan.id ? (
                    <Loader2 className="w-4 h-4 animate-spin mx-auto" />
                  ) : isCurrentPlan ? (
                    'Current Plan'
                  ) : currentPlan !== 'free' && plan.id === 'free' ? (
                    'Downgrade'
                  ) : (
                    'Upgrade'
                  )}
                </button>
              </div>
            )
          })}
        </div>
      </div>

      {/* Invoices */}
      <div className="glass-card p-6">
        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <FileText className="w-5 h-5 text-primary-400" />
          Billing History
        </h2>

        {invoices.length === 0 ? (
          <p className="text-dark-400 text-center py-8">
            No invoices yet
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-dark-700">
                  <th className="text-left py-3 px-4 text-dark-400 font-medium">Date</th>
                  <th className="text-left py-3 px-4 text-dark-400 font-medium">Amount</th>
                  <th className="text-left py-3 px-4 text-dark-400 font-medium">Status</th>
                  <th className="text-right py-3 px-4 text-dark-400 font-medium">Invoice</th>
                </tr>
              </thead>
              <tbody>
                {invoices.map((invoice) => (
                  <tr key={invoice.id} className="border-b border-dark-700/50">
                    <td className="py-3 px-4 text-white">{formatDate(invoice.date)}</td>
                    <td className="py-3 px-4 text-white">{formatPrice(invoice.amount)}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        invoice.status === 'paid'
                          ? 'bg-primary-500/20 text-primary-400'
                          : invoice.status === 'pending'
                          ? 'bg-amber-500/20 text-amber-400'
                          : 'bg-red-500/20 text-red-400'
                      }`}>
                        {invoice.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      {invoice.pdf_url && (
                        <a
                          href={invoice.pdf_url}
                          download
                          className="text-primary-400 hover:text-primary-300 inline-flex items-center gap-1"
                        >
                          <Download className="w-4 h-4" />
                          PDF
                        </a>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Payment Method */}
      <div className="glass-card p-6">
        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <CreditCard className="w-5 h-5 text-primary-400" />
          Payment Method
        </h2>
        
        <div className="flex items-center justify-between">
          <p className="text-dark-400">
            Payment processing is handled securely through Razorpay/Stripe
          </p>
          <button className="btn-secondary">
            Update Payment Method
          </button>
        </div>
      </div>
    </div>
  )
}
