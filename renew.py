from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyvirtualdisplay import Display
import undetected_chromedriver.v2 as uc
import sys
import pwn
import tldextract
import time
import yaml

username = ""
password = ""
domain = ""
delay = 10
page_timeout = 30
retry_backoff = 3
retry_delay = 10


def wait_load(driver, delay, type, value):
    WebDriverWait(driver, delay).until(
        EC.presence_of_element_located((type, value)))

def login(driver):
    driver.get(
        "https://sso.godaddy.com/v1/login?app=sso&path=%2Fv1%2Faccess&status=5")
    wait_load(driver, delay, By.ID, "username")
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "submitBtn").click()
    wait_load(driver, delay, By.CLASS_NAME, "access-now-button")


def delegate_access(driver):
    driver.get("https://account.godaddy.com/access")
    wait_load(driver, delay, By.CLASS_NAME, "access-now-button")
    driver.find_element(By.CLASS_NAME, "access-now-button").click()
    wait_load(driver, delay, By.CLASS_NAME, "headline-brand")


def add_record(driver, subdomain, record):
    driver.get("https://dcc.godaddy.com/control/dns?domainName={}".format(domain))
    wait_load(driver, delay, By.XPATH,
              "/html/body/div[2]/div/main/div/div/div[2]/div[4]/div/div[2]/span/div/div/button")

    # Click add record button
    driver.find_element(
        By.XPATH, "/html/body/div[2]/div/main/div/div/div[2]/div[4]/div/div[2]/span/div/div/button").click()

    # Click choose record type
    driver.find_element(
        By.XPATH, "/html/body/div[2]/div/main/div/div/div[2]/div[4]/div/div[3]/div/form/fieldset/div/div[1]/div/div/div[1]").click()

    # Click TXT record type
    driver.find_element(
        By.XPATH, "/html/body/div[2]/div/main/div/div/div[2]/div[4]/div/div[3]/div/form/fieldset/div/div[1]/div/div/div[2]/div[2]/div/a[5]").click()

    # Input subdomain
    driver.find_element(By.XPATH, "/html/body/div[2]/div/main/div/div/div[2]/div[4]/div/div[3]/div/form/fieldset/div/div[2]/div/div/div/input").send_keys(subdomain)

    # Input record
    driver.find_element(By.XPATH, "/html/body/div[2]/div/main/div/div/div[2]/div[4]/div/div[3]/div/form/fieldset/div/div[3]/div/div/div/input").send_keys(record)

    # Click save button
    driver.find_element(
        By.XPATH, "/html/body/div[2]/div/main/div/div/div[2]/div[4]/div/div[3]/div/form/div/div/button[1]").click()

    # Success notif
    wait_load(driver, delay, By.XPATH,
              "/html/body/div[10]/ul/li/div/div[1]/h2")


def delete_record(driver, subdomain):
    driver.get("https://dcc.godaddy.com/control/dns?domainName={}".format(domain))
    wait_load(driver, delay, By.XPATH,
              "/html/body/div[2]/div/main/div/div/div[2]/div[4]/div/div[2]/span/div/div/button")

    # Click Filter
    driver.find_element(
        By.XPATH, "/html/body/div[2]/div/main/div/div/div[2]/div[4]/div/div[2]/span/div/div/div[1]/button").click()

    # Click TXT  Filter
    driver.find_element(
        By.XPATH, "/html/body/div[2]/div/main/div/div/div[2]/div[4]/div/div[2]/span/div/div/div[1]/div/div[2]/div/span[5]").click()

    # Wait for filter finished
    # wait_load(driver, delay, By.XPATH, "/html/body/div[2]/div/main/div/div/div[2]/div[4]/div/div[3]/div/table/tbody/tr[1]/td[2]/div[1]/div[2]/span")
    time.sleep(5)

    # Delete record
    driver.find_element(By.XPATH, find_record_delete_xpath(
        driver, subdomain)).click()

    # Confirm delete
    wait_load(driver, delay, By.XPATH,
              "/html/body/div[10]/div/div/div[2]/div/div/button[1]")
    driver.find_element(
        By.XPATH, "/html/body/div[10]/div/div/div[2]/div/div/button[1]").click()

    # Success notif
    wait_load(driver, delay, By.XPATH,
              "/html/body/div[10]/ul/li/div/div[1]/h2")


def find_record_delete_xpath(driver, subdomain):
    trs = driver.find_elements(
        By.XPATH, "/html/body/div[2]/div/main/div/div/div[2]/div[4]/div/div[3]/div/table/tbody/tr")
    for i in range(len(trs)):
        if trs[i].find_element(By.XPATH, "td[3]").text == subdomain:
            return "/html/body/div[2]/div/main/div/div/div[2]/div[4]/div/div[3]/div/table/tbody/tr[{}]/td[6]/button".format(i + 1)

    # /html/body/div[2]/div/main/div/div/div[2]/div[4]/div/div[3]/div/table/tbody/tr[4]/td[3]
    # /html/body/div[2]/div/main/div/div/div[2]/div[4]/div/div[3]/div/table/tbody/tr[4]/td[6]/button
    # /html/body/div[2]/div/main/div/div/div[2]/div[4]/div/div[2]/span/div/div/div[1]/div/div[2]/div/span[5]/svg/use


def do_exit(driver, display, exit_code):
    driver.quit()
    display.stop()
    exit(exit_code)

# Not used currently


def bypass_detection(driver):
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument",
                           {
                               "source": """
            Object.defineProperty(navigator, 'maxTouchPoints', {get: () => 1});
            Object.defineProperty(navigator.connection, 'rtt', {get: () => 100});
            // https://github.com/microlinkhq/browserless/blob/master/packages/goto/src/evasions/chrome-runtime.js
            window.chrome = {
                app: {
                    isInstalled: false,
                    InstallState: {
                        DISABLED: 'disabled',
                        INSTALLED: 'installed',
                        NOT_INSTALLED: 'not_installed'
                    },
                    RunningState: {
                        CANNOT_RUN: 'cannot_run',
                        READY_TO_RUN: 'ready_to_run',
                        RUNNING: 'running'
                    }
                },
                runtime: {
                    OnInstalledReason: {
                        CHROME_UPDATE: 'chrome_update',
                        INSTALL: 'install',
                        SHARED_MODULE_UPDATE: 'shared_module_update',
                        UPDATE: 'update'
                    },
                    OnRestartRequiredReason: {
                        APP_UPDATE: 'app_update',
                        OS_UPDATE: 'os_update',
                        PERIODIC: 'periodic'
                    },
                    PlatformArch: {
                        ARM: 'arm',
                        ARM64: 'arm64',
                        MIPS: 'mips',
                        MIPS64: 'mips64',
                        X86_32: 'x86-32',
                        X86_64: 'x86-64'
                    },
                    PlatformNaclArch: {
                        ARM: 'arm',
                        MIPS: 'mips',
                        MIPS64: 'mips64',
                        X86_32: 'x86-32',
                        X86_64: 'x86-64'
                    },
                    PlatformOs: {
                        ANDROID: 'android',
                        CROS: 'cros',
                        LINUX: 'linux',
                        MAC: 'mac',
                        OPENBSD: 'openbsd',
                        WIN: 'win'
                    },
                    RequestUpdateCheckStatus: {
                        NO_UPDATE: 'no_update',
                        THROTTLED: 'throttled',
                        UPDATE_AVAILABLE: 'update_available'
                    }
                }
            }
            // https://github.com/microlinkhq/browserless/blob/master/packages/goto/src/evasions/navigator-permissions.js
            if (!window.Notification) {
                window.Notification = {
                    permission: 'denied'
                }
            }
            const originalQuery = window.navigator.permissions.query
            window.navigator.permissions.__proto__.query = parameters =>
                parameters.name === 'notifications'
                    ? Promise.resolve({ state: window.Notification.permission })
                    : originalQuery(parameters)
            const oldCall = Function.prototype.call
            function call() {
                return oldCall.apply(this, arguments)
            }
            Function.prototype.call = call
            const nativeToStringFunctionString = Error.toString().replace(/Error/g, 'toString')
            const oldToString = Function.prototype.toString
            function functionToString() {
                if (this === window.navigator.permissions.query) {
                    return 'function query() { [native code] }'
                }
                if (this === functionToString) {
                    return nativeToStringFunctionString
                }
                return oldCall.call(oldToString, this)
            }
            // eslint-disable-next-line
            Function.prototype.toString = functionToString
            """
                           })

    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        "source": """
        Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5]
        });
    """
    })


def load_creds():
    with open("creds.yaml", 'r') as stream:
        data_loaded = yaml.safe_load(stream)
    return data_loaded


if __name__ == "__main__":
    creds = load_creds()
    username = creds["username"]
    password = creds["password"]

    full_domain = sys.argv[1]
    dns_propagation_delay = int(sys.argv[2])
    ex = tldextract.extract(full_domain)
    domain = ex.registered_domain
    subdomain = "_acme-challenge.{}".format(ex.subdomain)

    # Renew request from certbot
    print("Requesting cert from LetsEncrypt..")
    p = pwn.process(["certbot", "-d", full_domain, "--dry-run",
                    "--manual", "--preferred-challenges", "dns", "certonly"])
    p.recvuntil(b"with the following value:")
    p.recvline()
    p.recvline()
    record = p.recvline().strip()
    print("Record: {}".format(record.decode('utf-8')))

    # Simulate X11 display
    display = Display(visible=0, size=(1920, 1080))
    display.start()

    print("Loading headless browser...")
    options = uc.ChromeOptions()
    options.arguments.extend(["--no-sandbox", "--disable-setuid-sandbox"])
    driver = uc.Chrome(headless=False, options=options, version_main=76)
    driver.set_page_load_timeout(page_timeout)
    print("Browser loaded")

    # bypass_detection(driver)
    # driver.get("https://bot.sannysoft.com/")
    # time.sleep(5)
    # driver.save_screenshot("screenshot.png")
    # time.sleep(1000)

    # Login
    print("Login...")
    for i in range(retry_backoff + 1):
        try:
            login(driver)
            print("Login success")
            break
        except:
            if retry_backoff - i + 1 == 1:
                print("Reached maximum retry {}, exiting...".format(retry_backoff))
                do_exit(driver, display, 1)
            print("Login failed, retrying in {} seconds".format(retry_delay))
            time.sleep(retry_delay)

    # Delegate access
    print("Delegating access...")
    for i in range(retry_backoff + 1):
        try:
            delegate_access(driver)
            print("Delegate access success")
            break
        except:
            if retry_backoff - i + 1 == 1:
                print("Reached maximum retry {}, exiting...".format(retry_backoff))
                do_exit(driver, display, 1)
            print("Delegate access failed, retrying in {} seconds".format(retry_delay))
            time.sleep(retry_delay)

    # Add record
    print("Adding record...")
    for i in range(retry_backoff + 1):
        try:
            add_record(driver, subdomain, record.decode('utf-8'))
            print("Add record success")
            break
        except:
            if retry_backoff - i + 1 == 1:
                print("Reached maximum retry {}, exiting...".format(retry_backoff))
                do_exit(driver, display, 1)
            print("Add record failed, retrying in {} seconds".format(retry_delay))
            time.sleep(retry_delay)

    # Wait for DNS propagation
    print(
        "Waiting for DNS propagation for {} seconds...".format(dns_propagation_delay))
    time.sleep(dns_propagation_delay)

    # Validate certbot
    p.sendline()

    # Delete record
    print("Deleting record...")
    for i in range(retry_backoff + 1):
        try:
            delete_record(driver, subdomain)
            print("Delete record success")
            break
        except:
            if retry_backoff - i + 1 == 1:
                print("Reached maximum retry {}, exiting...".format(retry_backoff))
                do_exit(driver, display, 1)
            print("Delete record failed, retrying in {} seconds".format(retry_delay))
            time.sleep(retry_delay)

    do_exit(driver, display, 0)
