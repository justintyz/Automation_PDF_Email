#!/usr/bin/env python3


import json
import locale
import sys
import emails
import reports

def load_data(filename):
  """Loads the contents of filename as a JSON file."""
  with open(filename) as json_file:
    data = json.load(json_file)
  return data


def format_car(car):
  """Given a car dictionary, returns a nicely formatted name."""
  return "{} {} ({})".format(car["car_make"], car["car_model"], car["car_year"])


def process_data(data):
  """Analyzes the data, looking for maximums.

  Returns a list of lines that summarize the information.
  """
  max_revenue = {"revenue": 0}
  max_sales = {"total_sales": 0}
  for item in data:
    # Calculate the revenue generated by this model (price * total_sales)
    item_price = locale.atof(item["price"].strip("$"))
    item_revenue = item["total_sales"] * item_price
    if item_revenue > max_revenue["revenue"]:
      item["revenue"] = item_revenue
      max_revenue = item
    summary = [
    "The {} generated the most revenue: ${:,.2f}".format(format_car(max_revenue["car"]), max_revenue["revenue"]),
    ]
    # Calculate the maximum sales from this model
    item_sales = item["total_sales"]
    if item_sales > max_sales["total_sales"]:
      item["total_sales"] = item_sales
      max_sales = item
    summary.append("The {} generated the most sales: {:,}".format(format_car(max_sales["car"]), max_sales["total_sales"]))

    # Calculate the most popular car_year
    year = set()
    data = load_data("../car_sales.json")
    for item in data:
      year.add(item['car']['car_year'])
    year_sales = {key: 0 for key in year}
    for item in data:
      if item['car']['car_year'] in year_sales:
        year_sales[item['car']['car_year']] += item["total_sales"]
    summary.append("The most popular year was {} with {:,} sales.".format(max(year_sales, key=year_sales.get), year_sales[max(year_sales, key=year_sales.get)]))
    

  

  return summary


def cars_dict_to_table(car_data):
  """Turns the data in car_data into a list of lists."""
  table_data = [["ID", "Car", "Price", "Total Sales"]]
  for item in car_data:
    table_data.append([item["id"], format_car(item["car"]), item["price"], item["total_sales"]])
  return table_data


def main(argv):
  """Process the JSON data and generate a full report out of it."""
  data = load_data("../car_sales.json")
  summary = process_data(data)
  additional_info = ""
  for line in summary:
    additional_info += line + "<br/>"

  # Attach the PDF to the email
  reports.generate("cars.pdf", "Sales Summary", additional_info, cars_dict_to_table(data))

  sender = "XXX@hotmail.com"
  # receiver = "{}@example.com".format(os.environ.get('USER'))
  receiver = "XXX@gmail.com"
  subject = "Sales Summary for last month"
  body = additional_info.replace("<br/>", "\n")

  message = emails.generate(sender, receiver, subject, body, "cars.pdf")
  emails.send(message)

if __name__ == "__main__":
    main(sys.argv)