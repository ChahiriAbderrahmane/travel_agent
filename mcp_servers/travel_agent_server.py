from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
import serpapi
import os
import re

load_dotenv()

api_key = os.getenv("Serp_API")
client = serpapi.Client(api_key=api_key)
mcp = FastMCP("SearchDestinationServer")

@mcp.tool()
def search_destination(destination: str) -> str:
    """Retrieves tourist attractions, landmarks, and activities for a given destination."""
    query = f"Top tourist attractions, landmarks, and things to do in {destination}"
    output = f"🌟 **Top Attractions in {destination}:**\n\n"
    
    try:
        results = client.search({
            "engine": "google",
            "q": query,
            "google_domain": "google.com",
            "hl": "en",
            "gl": "us"
        })

        if "top_sights" in results:
            sights = results["top_sights"].get("sights", [])[:5]
            for sight in sights:
                title = sight.get("title", "Unknown")
                description = sight.get("description", "No description available.")
                rating = sight.get("rating", "No rating")
                # Utilisation de += pour ajouter à la liste au lieu de l'écraser
                output += f"📍 **{title}**: {description} (Rating: {rating})\n\n"
                
        elif "organic_results" in results:
            for result in results["organic_results"][:4]:
                title = result.get("title", "Unknown")
                snippet = result.get("snippet", "No description available.")
                output += f"📍 **{title}**\n   {snippet}\n\n"
        else:
            return f"Could not find specific attractions for {destination}."

    except Exception as e:
        return f"An error occurred while fetching data: {str(e)}"

    return output.strip()


@mcp.tool()
def estimate_budget(destination: str, days: int) -> str:
    """Estimate travel budget in USD based on destination and duration of stay."""
    query = f"Average daily travel cost for person in {destination} in dollars"

    try:
        results = client.search({
            "engine": "google",
            "q": query,
            "google_domain": "google.com",
            "hl": "en",
            "gl": "us"
        })

        # On extrait le snippet pour l'utiliser comme source
        snippet = results.get("answer_box", {}).get("snippet") or results.get("organic_results", [{}])[0].get("snippet", "No source info")

        if "answer_box" in results and "snippet" in results["answer_box"]:
            answer = results["answer_box"]["snippet"]
            match = re.search(r"\$([\d,]+)", answer)
            if match:
                daily_cost = float(match.group(1).replace(",", ""))
                total_budget = daily_cost * days # Variable corrigée
                return (
                    f"💰 **Budget estimation for {destination} ({days} days)**\n"
                    f"- **Average daily cost :** ${daily_cost:,.2f}\n"
                    f"- **Total estimated cost :** ${total_budget:,.2f}\n\n"
                    f"*(Source: {snippet})*"
                )
        
        # Fallback si pas de chiffre exact trouvé
        return (
            f"💰 **Budget estimation for {destination}**\n"
            f"Could not extract an exact figure, but here's what the search says:\n"
            f"> {snippet}\n\n"
            f"A general rule of thumb is to budget around $150-$200 per day on average."
        )
    except Exception as e: # Ajout du bloc except manquant
        return f"An error occurred: {str(e)}"


@mcp.tool()
def get_weather(destination: str, travel_dates: str) -> str:
    """Get weather forecast for a destination during specified travel dates."""
    query = f"Weather forecast for {destination} during {travel_dates}"

    try:
        results = client.search({
            "engine": "google",
            "q": query,
            "google_domain": "google.com",
            "hl": "en",
            "gl": "us"
        })

        if "answer_box" in results and "snippet" in results["answer_box"]:
            weather_info = results["answer_box"]["snippet"]
            return f"🌤️ **Weather Forecast for {destination} ({travel_dates})**\n> {weather_info}"
        elif "organic_results" in results:
            weather_info = results["organic_results"][0].get("snippet", "")
            return f"🌤️ **Weather Info for {destination} ({travel_dates})**\n> {weather_info}"
        else:
            return f"Could not find weather forecast for {destination} during {travel_dates}."

    except Exception as e:
        return f"An error occurred while fetching weather data: {str(e)}"


@mcp.tool()
def currency_converter(amount: float, from_currency: str, to_currency: str) -> str:
    """Convert currency amount from one currency to another."""
    query = f"Convert {amount} {from_currency} to {to_currency}"

    try:
        results = client.search({
            "engine": "google",
            "q": query,
            "google_domain": "google.com",
            "hl": "en",
            "gl": "us"
        })

        # L'API SerpApi a souvent un widget spécifique pour les devises
        if "currency_converter" in results:
            to_amount = results["currency_converter"]["to"]["amount"]
            return f"💱 **Currency Conversion**\n{amount} {from_currency} = **{to_amount} {to_currency}**"
        elif "answer_box" in results and "answer" in results["answer_box"]:
            conversion_result = results["answer_box"]["answer"]
            return f"💱 **Currency Conversion**\n{conversion_result}"
        else:
            return f"Could not perform currency conversion for {amount} {from_currency} to {to_currency}."

    except Exception as e:
        return f"An error occurred while performing currency conversion: {str(e)}"


@mcp.tool()
def calculator_tool(expression: str) -> str:
    """Evaluate a mathematical expression and return the result."""
    try:
        # WARNING: eval can be dangerous. 
        result = eval(expression, {"__builtins__": {}})
        return f"🧮 **Calculator Result**\nThe result of `{expression}` is **{result}**"
    except Exception as e:
        return f"An error occurred while evaluating the expression: {str(e)}"
    

@mcp.tool()
def search_flights(origin: str, destination: str, departure_date: str, return_date: str) -> str:
    """Search for flights between origin and destination on specified dates."""
    query = f"Flights from {origin} to {destination} departing on {departure_date} and returning on {return_date}"

    try:
        results = client.search({
            "engine": "google",
            "q": query,
            "google_domain": "google.com",
            "hl": "en",
            "gl": "us"
        })

        if "answer_box" in results and "snippet" in results["answer_box"]:
            flight_info = results["answer_box"]["snippet"]
            return f"✈️ **Flight Search**\n> {flight_info}"
        elif "organic_results" in results:
            flight_info = results["organic_results"][0].get("snippet", "")
            return f"✈️ **Flight Search**\n> {flight_info}"
        else:
            return f"Could not find flight information for the specified route and dates."

    except Exception as e:
        return f"An error occurred while searching for flights: {str(e)}"

@mcp.tool()
def search_hotels(destination: str, check_in: str, check_out: str) -> str:
    """Search for hotels in a destination for specified check-in and check-out dates."""
    query = f"Hotels in {destination} from {check_in} to {check_out}"

    try:
        results = client.search({
            "engine": "google",
            "q": query,
            "google_domain": "google.com",
            "hl": "en",
            "gl": "us"
        })


        if "answer_box" in results and "snippet" in results["answer_box"]:
            hotel_info = results["answer_box"]["snippet"]
            return f"🏨 **Hotel Search**\n> {hotel_info}"
        elif "organic_results" in results:
            hotel_info = results["organic_results"][0].get("snippet", "")
            return f"🏨 **Hotel Search**\n> {hotel_info}"
        else:
            return f"Could not find hotel information for the specified destination and dates."

    except Exception as e:
        return f"An error occurred while searching for hotels: {str(e)}"
    
@mcp.tool()
def serach_anything(query: str) -> str:
    """Perform a general search for any query."""
    try:
        results = client.search({
            "engine": "google",
            "q": query,
            "google_domain": "google.com",
            "hl": "en",
            "gl": "us"
        })

        if "answer_box" in results and "snippet" in results["answer_box"]:
            search_info = results["answer_box"]["snippet"]
            return f"🔍 **Search Result**\n> {search_info}"
        elif "organic_results" in results:
            search_info = results["organic_results"][0].get("snippet", "")
            return f"🔍 **Search Result**\n> {search_info}"
        else:
            return f"No relevant information found for the query: {query}"

    except Exception as e:
        return f"An error occurred while performing the search: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")