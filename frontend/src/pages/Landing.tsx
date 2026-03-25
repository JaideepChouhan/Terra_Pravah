import { Link } from 'react-router-dom'
import { ArrowRightIcon } from '@heroicons/react/24/outline'

export default function Landing() {
  return (
    <div className="bg-background-light min-h-screen flex flex-col font-display antialiased text-text-main pt-20">

      {/* Hero Section */}
      <section className="flex-grow flex items-center pt-10 pb-20">
        <div className="max-w-7xl mx-auto w-full px-6 py-12 md:py-24 grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">
          {/* Left: Typography & CTA (60%) */}
          <div className="lg:col-span-7 flex flex-col gap-8 lg:pr-12">
            <h1 className="text-5xl md:text-6xl lg:text-[72px] font-black leading-[1.1] tracking-[-0.03em] text-text-main font-heading">
              Precision in <br className="hidden lg:block"/> Planetary Scale.
            </h1>
            <p className="text-lg md:text-xl text-muted max-w-2xl font-normal leading-relaxed">
              Translating complex climate solutions into accessible, premium offerings for enterprise and global sustainability leaders.
            </p>
            <div className="pt-4">
              <Link to="/register" className="btn-primary inline-flex items-center gap-2 group w-max">
                <span>Request Access</span>
                <ArrowRightIcon className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Link>
            </div>
          </div>

          {/* Right: Abstract Visualization (40%) */}
          <div className="lg:col-span-5 relative h-[400px] lg:h-[600px] w-full flex items-center justify-center bg-[#F7F3EB]/50 rounded-xl overflow-hidden border border-muted/10">
            {/* Abstract Topological Map SVG */}
            <svg aria-label="Abstract topological map animation" className="w-full h-full opacity-80" data-alt="Abstract topological lines animating" viewBox="0 0 500 500" xmlns="http://www.w3.org/2000/svg">
              <g className="text-primary/40" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path className="topo-path animate-draw-path" d="M -50 250 Q 150 100, 250 250 T 550 250"></path>
                <path className="topo-path animate-draw-path" d="M -50 300 Q 150 150, 250 300 T 550 300" style={{ animationDelay: "0.2s" }}></path>
                <path className="topo-path animate-draw-path" d="M -50 200 Q 150 50, 250 200 T 550 200" style={{ animationDelay: "0.1s" }}></path>
                <path className="topo-path animate-draw-path" d="M -50 350 Q 150 200, 250 350 T 550 350" style={{ animationDelay: "0.3s" }}></path>
                <path className="topo-path animate-draw-path" d="M -50 150 Q 150 0, 250 150 T 550 150" style={{ animationDelay: "0.4s" }}></path>
                <circle className="animate-pulse" cx="250" cy="250" fill="#e98963" r="4" stroke="none"></circle>
                <circle className="animate-pulse" cx="350" cy="180" fill="#e98963" r="3" stroke="none" style={{ animationDelay: "0.5s" }}></circle>
                <circle className="animate-pulse" cx="150" cy="320" fill="#e98963" r="2" stroke="none" style={{ animationDelay: "0.8s" }}></circle>
              </g>
            </svg>
          </div>
        </div>
      </section>

      {/* Mission Section */}
      <section id="mission" className="w-full flex flex-col bg-surface items-center py-20 md:py-32 px-4 md:px-8 relative z-10">
        <div className="max-w-[800px] w-full flex flex-col items-center text-center">
          <h4 className="text-primary text-[14px] font-display uppercase tracking-[2px] mb-8 font-medium">
            THE PHILOSOPHY
          </h4>
          <h1 className="text-text-inverse font-heading text-[32px] md:text-[48px] leading-[1.2] mb-16 md:mb-24">
            Grounding the technology in <i className="italic font-light">real-world</i> environmental impact.
          </h1>

          {/* Stats Grid */}
          <div className="w-full grid grid-cols-1 md:grid-cols-3 gap-12 md:gap-0">
            {/* Stat 1 */}
            <div className="flex flex-col items-start text-left md:pl-6 md:border-l md:border-muted/50 border-l border-muted/50 pl-6">
              <span className="text-primary text-[48px] md:text-[56px] font-heading leading-none mb-3">10M+</span>
              <span className="text-muted font-display text-base">Metrics Tracked</span>
            </div>

            {/* Stat 2 */}
            <div className="flex flex-col items-start text-left md:pl-6 md:border-l md:border-muted/50 border-l border-muted/50 pl-6">
              <span className="text-primary text-[48px] md:text-[56px] font-heading leading-none mb-3">50+</span>
              <span className="text-muted font-display text-base">Active Partners</span>
            </div>

            {/* Stat 3 */}
            <div className="flex flex-col items-start text-left md:pl-6 md:border-l md:border-muted/50 border-l border-muted/50 pl-6">
              <span className="text-primary text-[48px] md:text-[56px] font-heading leading-none mb-3">99.9%</span>
              <span className="text-muted font-display text-base">System Uptime</span>
            </div>
          </div>
        </div>
      </section>

      {/* Solutions Hub */}
      <section id="solutions" className="py-20 md:py-32 bg-background-light text-text-main px-4 md:px-10 z-10 relative">
        <div className="flex flex-col gap-20 max-w-[1200px] mx-auto">
          <div className="flex flex-col items-center text-center max-w-3xl mx-auto mb-10">
            <h1 className="text-4xl md:text-5xl font-black leading-tight tracking-[-0.033em] mb-6 font-heading">Solutions Hub</h1>
            <p className="text-lg text-muted">Comprehensive capabilities for planetary-scale environmental operations. Explore how our platform integrates with your infrastructure.</p>
          </div>

          {/* Feature 1 */}
          <div className="flex flex-col md:flex-row items-center gap-10 md:gap-20">
            <div className="w-full md:w-1/2 relative group rounded-sm overflow-hidden shadow-sm">
              <div className="aspect-[3/2] w-full bg-cover bg-center" style={{ backgroundImage: "url('https://lh3.googleusercontent.com/aida-public/AB6AXuAF_VPwP3-a6FNz-OJt4FSsxwQrBS2TjFnIfg8MrwNXYrf73-Cq-xC6qxyyFoBfOw8bnVSo7b4FXs3-BdqkOhNDh4NALsbifgh7s-LbpXkiyVqn3enw458DBnmsrsHprFckl3u9RfU1OxJElnP21wVUngpVXQ55Df1QgmF9mbqeazIzovC890As8tZ4IJvZ1VXTMjaz76WNdnZMY3scfcp1DU-G7wEYNPOFNtKShMjYuBKbiZqNKubfktfgLWnk9VWG8hlOYSACak_5')" }}></div>
              <div className="absolute inset-0 bg-accent/60 mix-blend-multiply transition-opacity duration-300 ease-in-out group-hover:opacity-0"></div>
            </div>
            <div className="w-full md:w-1/2 flex flex-col gap-6">
              <h2 className="text-[32px] font-bold leading-tight text-text-main font-heading">Global Emissions Tracking</h2>
              <ul className="em-dash-list flex flex-col gap-4 text-muted text-lg">
                <li>Real-time monitoring across all planetary scale operations</li>
                <li>Comprehensive coverage for Scope 1, 2, and 3 emissions</li>
                <li>Custom alert thresholds with automated anomaly detection</li>
                <li>Granular data filtering by facility, region, or product line</li>
              </ul>
            </div>
          </div>

          {/* Feature 2 */}
          <div className="flex flex-col md:flex-row-reverse items-center gap-10 md:gap-20">
            <div className="w-full md:w-1/2 relative group rounded-sm overflow-hidden shadow-sm">
              <div className="aspect-[3/2] w-full bg-cover bg-center" style={{ backgroundImage: "url('https://lh3.googleusercontent.com/aida-public/AB6AXuDXpNQSzLCtX9geI8A9VPdNOY4cZ3EehT7AfrPtFcS1toZORJnyb7k0C3zN5EQU5BceLXyMFqchGfl0M8pRWx05T5dk5T6ME4_PDBG1Kc31GvqAa8Fp2UbxhbHSKg3XQ2s5vzeY6ITPWDKwThNuokm-25egqzNDL_m5UjpGocgvgTbk0fg_2pau5NBoHsSg7KnB0RxoY8mFHXJbZ7Vrb_PopucZSBm2HwZBX6BO6g9C9jllrBpCm-qSm62rW1fo2MBWQO5MyacJYdy6')" }}></div>
              <div className="absolute inset-0 bg-accent/60 mix-blend-multiply transition-opacity duration-300 ease-in-out group-hover:opacity-0"></div>
            </div>
            <div className="w-full md:w-1/2 flex flex-col gap-6">
              <h2 className="text-[32px] font-bold leading-tight text-text-main font-heading">Supply Chain Analytics</h2>
              <ul className="em-dash-list flex flex-col gap-4 text-muted text-lg">
                <li>Deep-tier vendor integration and performance scoring</li>
                <li>Predictive risk modeling for environmental disruptions</li>
                <li>Material lifecycle traceability from origin to end-of-life</li>
                <li>Automated supplier compliance auditing tools</li>
              </ul>
            </div>
          </div>

          {/* Feature 3 */}
          <div className="flex flex-col md:flex-row items-center gap-10 md:gap-20">
            <div className="w-full md:w-1/2 relative group rounded-sm overflow-hidden shadow-sm">
              <div className="aspect-[3/2] w-full bg-cover bg-center" style={{ backgroundImage: "url('https://lh3.googleusercontent.com/aida-public/AB6AXuDdmqEIPsD1yI-lRe5noxigSX8oJejNqP4Aq5g623tEuVAgefv9NnLMhP3SSP_pl2X6sNfy6lKEvB1Xl_aroaWVgqyqLu92wbK47NonbN6TmpO9TpV4nqtO3yykzISjKLwg-93iwvM4Ayq4BsA-yDxdz13pRL_v03g3OJPdx4VN2CxPCI7rNXgwq4QQRnC_LYmxp6YeDYUFnwpIM4qpdwwf2TdFfj3NZvINx5sNvqVzw6j_P0Wkdo7n1gae6j4Jm_6rE-ooC8nxCQ3O')" }}></div>
              <div className="absolute inset-0 bg-accent/60 mix-blend-multiply transition-opacity duration-300 ease-in-out group-hover:opacity-0"></div>
            </div>
            <div className="w-full md:w-1/2 flex flex-col gap-6">
              <h2 className="text-[32px] font-bold leading-tight text-text-main font-heading">Automated ESG Reporting</h2>
              <ul className="em-dash-list flex flex-col gap-4 text-muted text-lg">
                <li>One-click generation for global compliance frameworks</li>
                <li>Auditor-ready documentation with full data provenance</li>
                <li>Interactive stakeholder sharing portals</li>
                <li>Continuous alignment with evolving regulatory standards</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Case Studies */}
      <section id="cases" className="py-20 md:py-32 bg-background-light px-4 md:px-10 lg:px-20 overflow-hidden relative z-10 border-t border-muted/20">
        <div className="max-w-[1440px] w-full mx-auto flex flex-col">

          {/* Header */}
          <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 gap-6">
            <div className="max-w-2xl">
              <h2 className="font-heading text-4xl md:text-5xl lg:text-6xl text-text-main tracking-tight leading-none mb-4">Tested by Pioneers</h2>
              <p className="text-muted text-lg md:text-xl font-display max-w-lg">
                See how enterprise leaders are using our platform to drive planetary-scale analytics.
              </p>
            </div>
            {/* Track Controls (Desktop/Tablet) */}
            <div className="hidden md:flex gap-4">
              <button aria-label="Previous case study" className="w-12 h-12 flex items-center justify-center border border-surface text-surface hover:bg-surface hover:text-text-inverse transition-colors duration-300 group focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-background-light">
                <span className="material-symbols-outlined text-2xl font-light group-hover:-translate-x-1 transition-transform duration-300">arrow_left_alt</span>
              </button>
              <button aria-label="Next case study" className="w-12 h-12 flex items-center justify-center border border-surface text-surface hover:bg-surface hover:text-text-inverse transition-colors duration-300 group focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-background-light">
                <span className="material-symbols-outlined text-2xl font-light group-hover:translate-x-1 transition-transform duration-300">arrow_right_alt</span>
              </button>
            </div>
          </div>

          {/* Testimonial Track */}
          <div className="flex overflow-x-auto no-scrollbar snap-x snap-mandatory md:snap-none pb-8 -mx-4 px-4 md:mx-0 md:px-0 gap-6 md:gap-8 cursor-grab active:cursor-grabbing">
            {/* Card 1 */}
            <div className="flex-none w-[85vw] md:w-[500px] lg:w-[600px] bg-white border border-muted/30 p-8 md:p-12 flex flex-col justify-between snap-center min-h-[400px]">
              <div>
                <span className="text-primary text-4xl mb-6 opacity-50 block font-serif">&quot;</span>
                <p className="font-heading italic text-2xl md:text-3xl text-text-main leading-snug mb-8">
                  &quot;This technology has fundamentally transformed our approach to planetary scale analytics. The precision is unmatched in the industry.&quot;
                </p>
              </div>
              <div className="flex items-center justify-between border-t border-muted/30 pt-6 mt-auto">
                <div>
                  <p className="font-display font-medium text-text-main text-lg">Jane Doe</p>
                  <p className="font-display text-muted text-sm">Chief Climate Officer</p>
                </div>
                <div className="h-8 w-24 bg-accent/20 flex items-center justify-center grayscale opacity-70">
                  <span className="text-xs font-heading font-bold text-surface tracking-widest uppercase">Acme Corp</span>
                </div>
              </div>
            </div>

            {/* Card 2 */}
            <div className="flex-none w-[85vw] md:w-[500px] lg:w-[600px] bg-white border border-muted/30 p-8 md:p-12 flex flex-col justify-between snap-center min-h-[400px]">
              <div>
                <span className="text-primary text-4xl mb-6 opacity-50 block font-serif">&quot;</span>
                <p className="font-heading italic text-2xl md:text-3xl text-text-main leading-snug mb-8">
                  &quot;A reliable, established partner in our ESG journey. Terra Pravah delivers precision data that our investors trust unconditionally.&quot;
                </p>
              </div>
              <div className="flex items-center justify-between border-t border-muted/30 pt-6 mt-auto">
                <div>
                  <p className="font-display font-medium text-text-main text-lg">John Smith</p>
                  <p className="font-display text-muted text-sm">VP of ESG Investment</p>
                </div>
                <div className="h-8 w-24 bg-accent/20 flex items-center justify-center grayscale opacity-70">
                  <span className="text-xs font-heading font-bold text-surface tracking-widest uppercase">GlobalFund</span>
                </div>
              </div>
            </div>

            {/* Card 3 */}
            <div className="flex-none w-[85vw] md:w-[500px] lg:w-[600px] bg-white border border-muted/30 p-8 md:p-12 flex flex-col justify-between snap-center min-h-[400px]">
              <div>
                <span className="text-primary text-4xl mb-6 opacity-50 block font-serif">&quot;</span>
                <p className="font-heading italic text-2xl md:text-3xl text-text-main leading-snug mb-8">
                  &quot;The insights we've gained have been invaluable for our sustainability managers. It's not just data; it's a clear roadmap.&quot;
                </p>
              </div>
              <div className="flex items-center justify-between border-t border-muted/30 pt-6 mt-auto">
                <div>
                  <p className="font-display font-medium text-text-main text-lg">Alice Johnson</p>
                  <p className="font-display text-muted text-sm">Director of Sustainability</p>
                </div>
                <div className="h-8 w-24 bg-accent/20 flex items-center justify-center grayscale opacity-70">
                  <span className="text-xs font-heading font-bold text-surface tracking-widest uppercase">EcoLogix</span>
                </div>
              </div>
            </div>

            {/* Spacer for right padding on scroll */}
            <div className="hidden md:block flex-none w-[10vw]"></div>
          </div>
        </div>
      </section>

    </div>
  )
}
