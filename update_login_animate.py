import sys

with open('frontend/src/pages/auth/Login.tsx', 'r') as f:
    code = f.read()

if 'from "framer-motion"' not in code and "from 'framer-motion'" not in code:
    code = code.replace("import { ArrowRightIcon }", "import { motion } from 'framer-motion'\nimport { ArrowRightIcon }")

code = code.replace(
    '<main className="w-full max-w-[400px] mx-auto px-6 py-16 md:py-24 flex flex-col items-center">',
    '''<motion.main 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className="w-full max-w-[400px] mx-auto px-6 py-16 md:py-24 flex flex-col items-center"
    >'''
)
code = code.replace('</main>', '</motion.main>')

with open('frontend/src/pages/auth/Login.tsx', 'w') as f:
    f.write(code)
    
print("updated login animation")
