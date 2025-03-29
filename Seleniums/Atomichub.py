from time import sleep

from selenium.common.exceptions import StaleElementReferenceException, NoSuchWindowException

from Alert import say
from Colors import printc
from Seleniums.WaxSel import check_wax_approve
from Telegrams import message
from Times import now, elapsed_seconds
from Wax import whitelist_wam_account


def transfert_nft(browser, name_to: str, nft_ids: list[int | str]):
    try:
        browser.print(("atomichub_transfert_nft", name_to, nft_ids, False))
        if not whitelist_wam_account(name_to):
            raise ValueError("Wam account is not whitelisted")
        url_transfert = r"https://wax.atomichub.io/trading/transfer?asset_id=" + ",".join(map(str, nft_ids))
        browser.new_page(url_transfert)
        accept_cooki_btn_xpath = "/html/body/div[3]/div/div/div/div[2]/button[1]"
        accept_cooki_btn = browser.get_element(accept_cooki_btn_xpath)
        if accept_cooki_btn is not None:
            browser.element_click(accept_cooki_btn)
        login_xpath = "/html/body/div/div[2]/div/div/div/div[2]/div[3]/button"
        cloud_wallet_xpath = "/html/body/div[3]/div/div/div[2]/div[1]/div[1]/div/button"
        login_txt = browser.get_locator_text(url_transfert, login_xpath)
        start = now()
        while login_txt is not None and login_txt == "LOGIN":
            if elapsed_seconds(start) >= 5:
                printc(login_txt, background_color="red")
                # say(browser.name + " have to login")
                browser.get_element_n_click(login_xpath)
                cloud_wallet = browser.wait_element(url_transfert, cloud_wallet_xpath)
                browser.element_click(cloud_wallet)
                check_wax_approve(browser)
            sleep(1)
            login_txt = browser.get_locator_text(url_transfert, login_xpath)
        login_txt = browser.get_locator_text(url_transfert, login_xpath)
        if login_txt is not None and login_txt == "LOGIN":
            browser.get_element_n_click(login_xpath)
        input_to_xpath_1 = "/html/body/div/div[3]/div/div[2]/div[2]/div[3]/table/tbody/tr[1]/td[2]/div/div/div/input"
        input_to_xpath_2 = "/html/body/div/div[3]/div/div[3]/div[2]/div[3]/table/tbody/tr[1]/td[2]/div/div/div/input"
        input_to_xpath = [input_to_xpath_1, input_to_xpath_2]
        check_wax_approve(browser)
        browser.wait_element(url_transfert, input_to_xpath, refresh=10)
        input_to = browser.get_element(input_to_xpath)
        browser.clear_send(input_to)
        browser.element_send(input_to, name_to)
        send_transfer_button_xpath_1 = "/html/body/div/div[3]/div/div[2]/div[2]/div[3]/div/div[2]/button"
        send_transfer_button_xpath_2 = "/html/body/div/div[3]/div/div[3]/div[2]/div[3]/div/div[2]/button"
        send_transfer_button_xpath = [send_transfer_button_xpath_1, send_transfer_button_xpath_2]
        send_transfer_button = browser.wait_element(url_transfert, send_transfer_button_xpath, refresh=10)
        start = now()
        while not send_transfer_button.is_enabled():
            if elapsed_seconds(start) >= 15:
                browser.print("\tvalidate_button_is_not_enabled")
                sleep(1)
                return False
        browser.element_click(send_transfer_button)
        confirm_button_xpath_1 = "/html/body/div[3]/div/div/div[2]/div[2]/div/button"
        confirm_button_xpath_2 = "/html/body/div[4]/div/div/div[2]/div[2]/div/button"
        confirm_button_xpaths = [confirm_button_xpath_1, confirm_button_xpath_2]
        browser.wait_element(url_transfert, confirm_button_xpaths)
        transaction_message_xpath_1 = "/html/body/div[3]/div/div/div/div[2]/div[1]"
        transaction_message_xpath_2 = "/html/body/div[4]/div/div/div/div[2]/div[1]"
        start = now()
        while True:
            transaction_message_text = browser.get_locator_text(url_transfert, [transaction_message_xpath_1, transaction_message_xpath_2])
            if transaction_message_text is not None and "Transaction Successful!".lower() in transaction_message_text.lower():
                return True
            elif transaction_message_text and transaction_message_text.lower() == "confirm":
                confirm_button = browser.get_element(confirm_button_xpaths)
                browser.element_click(confirm_button)
            sleep(1)
            check_wax_approve(browser)
            # if elapsed_seconds(start) >= 3 * 60:
            #     return True
                # sleep(1)
            if elapsed_seconds(start) >= 60:
                message(browser.name + " check wax transfert")
                return True
                # say(browser.name + " wax approve have to validate transfert")
                # sleep(1)
        sleep(1)
    except StaleElementReferenceException or NoSuchWindowException:
        browser.relaunch_n_connect()
        return transfert_nft(browser, name_to, nft_ids)
