import re

def get_sections(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    sections = re.findall(r'\\(?:section|subsection|subsubsection)\{([^}]+)\}', content)
    return sections

eng = get_sections('/Users/andyhuang/Desktop/毕业设计相关文档/我的毕设/paper/main.tex')
chi = get_sections('/Users/andyhuang/Desktop/毕业设计相关文档/我的毕设/paper-Chinese/main.tex')

print("English Sections:")
for s in eng: print("  " + s)

print("\nChinese Sections:")
for s in chi: print("  " + s)
