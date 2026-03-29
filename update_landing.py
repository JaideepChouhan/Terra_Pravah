import sys

with open("frontend/src/pages/Landing.tsx", "r") as f:
    code = f.read()

# Add framer-motion import if not present
if "from 'framer-motion'" not in code:
    code = code.replace("import { Link } from 'react-router-dom'", "import { Link } from 'react-router-dom'\nimport { motion } from 'framer-motion'")

# Add motion.div to Hero Section left part
code = code.replace("""<div className="lg:col-span-7 flex flex-col gap-8 lg:pr-12">""", """<motion.div 
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="lg:col-span-7 flex flex-col gap-8 lg:pr-12"
          >""")
code = code.replace("""          {/* Right: Abstract Visualization (40%) */}""", """          </motion.div>
          {/* Right: Abstract Visualization (40%) */}""")
# And remove the original closing div for left part
code = code.replace("""            </div>\n          </div>\n\n          {/* Right: Abstract Visualization (40%) */}""", """            </div>\n\n          {/* Right: Abstract Visualization (40%) */}""") # Quick hack fix, let's do more robust

with open("frontend/src/pages/Landing.tsx", "w") as f:
    f.write(code)
