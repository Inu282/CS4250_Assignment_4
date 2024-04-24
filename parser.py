from pymongo import MongoClient
from bs4 import BeautifulSoup

client = MongoClient("mongodb://localhost:27017/")
db = client["web_crawler"]

pages_collection = db["pages"]
professors_collection = db["professors"]

faculty_page = pages_collection.find_one(
    {"url": "https://www.cpp.edu/sci/computer-science/faculty-and-staff/permanent-faculty.shtml"}
)

if not faculty_page:
    print("Permanent Faculty page not found in the database.")
else:
    html_content = faculty_page["html"]
    soup = BeautifulSoup(html_content, "html.parser")

    faculty_divs = soup.find_all("div", class_="clearfix")

    if not faculty_divs:
        print("No faculty information found. Please check the structure.")
    else:
        for faculty_div in faculty_divs:
            professor_data = {}

            name_tag = faculty_div.find("h2")
            professor_data["name"] = name_tag.text.strip() if name_tag else "Unknown"

            details = faculty_div.find("p")

            if details:
                strong_tags = details.find_all("strong")

                title_tag = next(
                    (tag for tag in strong_tags if "Title" in tag.text),
                    None
                )
                professor_data["title"] = title_tag.next_sibling.strip() if title_tag else "Unknown"

                office_tag = next(
                    (tag for tag in strong_tags if "Office" in tag.text),
                    None
                )
                professor_data["office"] = office_tag.next_sibling.strip() if office_tag else "Unknown"

                phone_tag = next(
                    (tag for tag in strong_tags if "Phone" in tag.text),
                    None
                )
                professor_data["phone"] = phone_tag.next_sibling.strip() if phone_tag else "Unknown"

                email_tag = details.find("a", href=lambda x: x and "mailto:" in x)
                professor_data["email"] = email_tag["href"].replace("mailto:", "") if email_tag else "Unknown"

                website_tag = details.find("a", href=lambda x: x and "http" in x)
                professor_data["website"] = website_tag["href"] if website_tag else "Unknown"

            professors_collection.insert_one(professor_data)

        print("All faculty information has been successfully stored in MongoDB.")
