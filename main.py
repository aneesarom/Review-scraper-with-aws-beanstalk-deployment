from bs4 import BeautifulSoup
from flask import Flask, render_template, request
import requests
import logging

# debug will make work all the logging methods
logging.basicConfig(filename="example.log", level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/review", methods=["GET", "POST"])
def review():
    reviews_dict = []
    redirect_url = ""
    if request.method == "POST":
        try:
            search = request.form["content"]
            url = f"https://www.flipkart.com/search?q={search}"
            front_response = requests.get(url)
            front_soup = BeautifulSoup(front_response.text, "html.parser")
            big_box = front_soup.find_all("div", class_="_1AtVbE col-12-12")
            logging.info("Succesfully connected big_box")

            for num in range(len(big_box)):
                try:
                    redirect_url = big_box[num].div.div.div.a["href"]
                    break
                except Exception as err:
                    logging.info("Div is not available")

            product_url = url + redirect_url
            product_response = requests.get(product_url)
            product_soup = BeautifulSoup(product_response.text, "html.parser")
            logging.info("Sucessfully entered product page")
            try:
                product_name_tag = product_soup.find(name="span", class_="B_NuCI")
                comment_tag = product_soup.find_all(name="div", class_="t-ZTKy")
                rating_tag = product_soup.find_all(name="div", class_="_3LWZlK _1BLPMq")
                customer_name_tag = product_soup.find_all(name="p", class_="_2sc7ZR _2V5EHH")
                comment_head_tag = product_soup.find_all(name="p", class_="_2-N8zT")
                logging.info("Able to access the product tags")
                for i in range(len(rating_tag)):
                    product = product_name_tag.text
                    comment = comment_tag[i].text.strip("READ MORE")
                    rating = rating_tag[i].text
                    customer_name = customer_name_tag[i].text
                    comment_head = comment_head_tag[i].text
                    dic = {
                        "Product": product,
                        "Comment": comment,
                        "Rating": rating,
                        "CommentHead": comment_head,
                        "Name": customer_name
                    }
                    reviews_dict.append(dic)
                return render_template("result.html", reviews=reviews_dict)
            except Exception as err:
                logging.info(f"Error accessing the tags in product page: {err}")
                return render_template("index.html")
        except Exception as error:
            logging.info(f"There is issue in accessing the website: {error}")
            return render_template("index.html")
    elif request.method == "GET":
        return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)


