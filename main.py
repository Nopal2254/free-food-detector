from playwright.sync_api import sync_playwright
from plyer import notification
import time

# Define the groups to monitor
GROUP_NAME = [
    "Enter Your Group Name Here",
    "Free Food Group",
    "Food Sharing Group"
]
# Define keywords in multiple languages
KEYWORDS = [#English
            "free","food","meal",
            #Turkish
            "ikram","ücretsiz",
            #Indonesian
            "gratis"
    ]
last_alert_time = {}
COOLDOWN = 60 #Seconds

now = time.time()

def contain_keyword(text):
    text = text.lower()
    return any(word in text for word in KEYWORDS)

def open_group(page,gruoup_name):
    search_box = page.locator("[aria-label*='Search']").first
    search_box.click()
    search_box.fill(gruoup_name)
    time.sleep(1)
    page.keyboard.press("Enter")
    time.sleep(1)

def send_notification(group,message):
    notification.notify(
        title=f"🍕 Free Food Alert - {group}",
        message=message[:100],
        timeout=5
    )

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context() #keep session alive
        page = context.new_page()

        print("Opening WhatsApp Web...")
        page.goto("https://web.whatsapp.com")

        print("Please scan QR code ...")
        page.wait_for_selector("[data-testid='chat-list']", timeout=60000)
        print("Logged in successfully!")

        #Store last chat count for each group
        last_count = {group: 0 for group in GROUP_NAME}

        while True:
            for group in GROUP_NAME:
                try:
                    open_group(page,group)
                    print(f"Checking group: {group}")

                    messages = page.locator("div.message-in")
                    count = messages.count()

                    if count > last_count[group]:
                        for i in range(last_count[group],count):
                            msg = messages.nth(i)

                            try:
                                text = msg.inner_text()
                            except:
                                continue
                            if not text.strip():
                                continue

                            print(f"{group} - New message: {text}")

                            if contain_keyword(text):
                                last_time = last_alert_time.get(group, 0)

                                if now - last_time > COOLDOWN:
                                    send_notification(group,text)   #Send notification
                                    last_alert_time[group] = now
                        
                        last_count[group] = count
                except Exception as e:
                    print(f"Error in group {group}: {e}")

                time.sleep(2)
            time.sleep(2) #wait before checking groups again                    

if __name__ == "__main__":
    main()