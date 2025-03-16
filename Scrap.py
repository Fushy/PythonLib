def html_structure(element, indent=0):
    result = ""
    if element.name:
        attrs_str = ' '.join(f'{k}="{v}"' for k, v in element.attrs.items())
        result += ' ' * indent + f'<{element.name} {attrs_str}>'
        for child in element.children:
            result += html_structure(child, indent + 2)
        result += ' ' * indent + f'</{element.name}>\n'
    return result

def soup_to_files(soup):
    with open("soup.txt", "w", encoding="utf-8") as file:
        file.write(soup.prettify())
    with open("soup.html", "w", encoding="utf-8") as file:
        file.write(str(soup))
    with open("soup_structure.txt", "w", encoding="utf-8") as file:
        file.write(html_structure(soup, indent=0))
