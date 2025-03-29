from time import sleep

from selenium.webdriver.common.keys import Keys

from Alert import say
from Introspection import frameinfo
from Regex import search_n_get_float
from Seleniums.ClassesSel import Browser
from Seleniums.Selenium import get_element_text, get_element_class
from Seleniums.WaxSel import check_wax_approve
from Telegrams import message
from Times import elapsed_seconds, now, elapsed_minutes
from Wax import whitelist_wam_account

ALCOR_TRANSFERT_URL = "https://wax.alcor.exchange/wallet"
ALCOR_MARKETS_URL = "https://wax.alcor.exchange/markets"
ALCOR_URL = "https://wax.alcor.exchange/"

alcor_trade_url = "https://wax.alcor.exchange/trade/"
devise_xpath = "/html/body/div[1]/div/div/div[4]/div/div[2]/div/div[5]/div[2]/div/div[2]/div[1]/div/div/div[1]/div/small[2]"
my_tokens_xpath = "/html/body/div[1]/div/div/div[4]/div/div[2]/div/div[5]/div[2]/div/div[2]/div[1]/div/div/div[2]/div/small[2]"
existing_trades_xpath = "/html/body/div[1]/div/div/div[4]/div/div[2]/div/div[4]/div[2]/div[2]/div[1]/div/div[3]/table/tbody"
cancel_all_orders_xpath = "/html/body/div[1]/div/div/div[4]/div/div[2]/div/div[4]/div[2]/div[2]/div[1]/div/div[2]/table/thead/tr/th[7]/div/span[2]"


def connect(browser: Browser, new_page=True) -> bool:
    browser.print("login_alcor", False)
    if new_page:
        browser.new_page(ALCOR_TRANSFERT_URL)
    search_asset_xpath_1 = "/html/body/div[1]/div/div/div[4]/div/div[3]/div/div[2]/div/div[2]/table/thead/tr/th[1]/div"
    if browser.wait_text(ALCOR_TRANSFERT_URL, [search_asset_xpath_1]) != "Asset":
        return False
    verif_n_connect(browser)
    connect_wallet_xpath = "/html/body/div/div/div/div[4]/nav/div[2]/div/div[2]/button[1]"
    if browser.get_text(ALCOR_TRANSFERT_URL, connect_wallet_xpath) == "Connect Wallet":
        return False
    return True


def verif_n_connect(browser):
    connect_wallet_xpath = "/html/body/div[1]/div/div/nav/div[2]/div/div[2]/button[1]"
    if browser.get_locator_text(ALCOR_URL, connect_wallet_xpath) == "Connect Wallet":
        wallet_connect_xpath = "/html/body/div[1]/div/div/nav/div[2]/div/div[2]/button[1]"
        wallet_connect = browser.get_element(wallet_connect_xpath)
        browser.element_click(wallet_connect)
        wallet_wax_xpath = "/html/body/div[3]/div/div[2]/div/div[1]/div[1]/button"
        wallet_wax = browser.get_element(wallet_wax_xpath)
        browser.element_click(wallet_wax)
        sleep(1)
        check_wax_approve(browser)
    name_xpath_1 = "/html/body/div[1]/div/div/nav/div[2]/div/div[2]/div/div[2]/div"
    check_wax_approve(browser)
    if not browser.wait_element(ALCOR_URL, [name_xpath_1]):
        return False
    return True


def transaction(browser: Browser,
                to: str,
                amount: float,
                token_send: str,
                memo: str = None,
                send_msg: bool = False) -> bool:
    """ amount = -1 <=> max """
    if amount == 0 or browser.name == to:
        return True
    name = browser.name
    browser.print(("transaction", to, amount, token_send, memo), False)
    if not whitelist_wam_account(to, memo):
        raise ValueError("Wam account is not whitelisted")
    connect(browser)
    tokens_container_xpath_1 = "/html/body/div[1]/div/div/div[3]/div/div[4]/div/div[2]/div/div[3]/table/tbody"
    tokens_container = browser.wait_element(ALCOR_TRANSFERT_URL, [tokens_container_xpath_1])
    if not tokens_container:
        return False
    # search_input_xpath = "/html/body/div/div/div/div[4]/div/div/div[7]/div/div[1]/div/input"
    # search_input = browser.get_element(search_input_xpath)
    # if search_input is None:
    #     return False
    # browser.element_send(search_input, token_send)
    tokens_tag = "tr"
    old_tokens_len = len(tokens_container.find_elements_by_tag_name(tokens_tag))
    while True:
        sleep(1)
        tokens = tokens_container.find_elements_by_tag_name(tokens_tag)
        if len(tokens) == old_tokens_len:
            break
        old_tokens_len = len(tokens)
    # i = 1 - 4
    token_text = ""
    token = None
    for token in tokens:
        token_text = get_element_text(token)
        if token_send in token_text:
            break
        # i += 4
    if token_send not in token_text:
        browser.print(("not_found_token", to, amount, token_send, memo))
        market_button_xpath1 = "/html/body/div[1]/div/div/nav/div[1]/ul/li[2]"
        browser.get_element_n_click([market_button_xpath1])
        search_token_xpath1 = "/html/body/div[1]/div/div/div[3]/div/div[4]/div/div[1]/div/input"
        browser.wait_element(ALCOR_URL, [search_token_xpath1])
        tokens_container = browser.wait_element(ALCOR_MARKETS_URL, [tokens_container_xpath_1])
        if not tokens_container:
            return False
        tokens_tag = "tr"
        old_tokens_len = len(tokens_container.find_elements_by_tag_name(tokens_tag))
        while True:
            sleep(1)
            tokens = tokens_container.find_elements_by_tag_name(tokens_tag)
            if len(tokens) == old_tokens_len:
                break
            old_tokens_len = len(tokens)
        token_text = ""
        token = None
        for token in tokens:
            token_text = get_element_text(token)
            if token_send in token_text:
                break
        if token_send not in token_text:
            return False
        browser.element_click(token)
        sleep(1)
        wallet_header_title_xpath1 = "/html/body/div[1]/div/div/nav/div[1]/ul/li[5]"
        browser.get_element_n_click([wallet_header_title_xpath1])
        sleep(1)
    tokens_container = browser.wait_element(ALCOR_URL, [tokens_container_xpath_1])
    if not tokens_container:
        return False
    tokens_tag = "tr"
    old_tokens_len = len(tokens_container.find_elements_by_tag_name(tokens_tag))
    while True:
        sleep(1)
        tokens = tokens_container.find_elements_by_tag_name(tokens_tag)
        if len(tokens) == old_tokens_len:
            break
        old_tokens_len = len(tokens)
    token_text = ""
    token = None
    for token in tokens:
        token_text = get_element_text(token)
        if token_send in token_text:
            break
    if token_send not in token_text:
        return False
    transfert_class = "el-button"
    action_buttons = token.find_elements_by_class_name(transfert_class)
    if action_buttons is None:
        return False
    transfert_button = action_buttons[1]
    tokens_xpath_1 = "/html/body/div[1]/div/div/div[3]/div/div[4]/div/div[4]/div/div[2]/form/div[2]/div/span/button/span"
    start = now()
    while True:
        if elapsed_seconds(start) > 30:
            return False
        browser.element_click(transfert_button)
        token_text = browser.wait_text(ALCOR_TRANSFERT_URL, [tokens_xpath_1], leave=2)
        if token_text is not None:
            break
    tokens = search_n_get_float(token_text)
    if tokens is None:
        return False
    browser.print(("token_send", token_send, tokens))
    if float(tokens) < float(amount):
        browser.print(("not_enough_tokens", tokens, "<", amount))
        return True
    inputs_xpath_1 = "/html/body/div[1]/div/div/div[3]/div/div[4]/div/div[4]/div/div[2]/form"
    inputs_xpath_2 = "/html/body/div[1]/div/div/div[4]/div/div/div[7]/div/div[4]/div/div[2]/form"
    inputs = browser.get_element([inputs_xpath_1, inputs_xpath_2]).find_elements_by_class_name("el-input__inner")
    adress_to = inputs[0]
    amount_send = inputs[1]
    memo_send = inputs[2]
    browser.element_send(adress_to, to)
    if memo is not None:
        browser.element_send(memo_send, memo)
    amount_send_tokens = tokens if amount == -1 else amount
    browser.element_send(amount_send, Keys.BACK_SPACE, amount_send_tokens)
    send_transfer_class = "el-button.w-100.done.el-button--primary"
    sleep(1)
    send_transfer = browser.get_element(send_transfer_class, browser.driver.find_element_by_class_name)
    browser.element_click(send_transfer)
    # laaa
    browser.print(("transaction_sent", to, amount, token_send, memo))
    check_wax_approve(browser)
    body_xpath = "/html/body"
    # msgbox_header_xpath = "/html/body/div[3]/div/div[1]/div"
    msgbox_header_xpath = "/html/body/div[4]/div"
    msgbox_header = None
    start = now()
    while not msgbox_header:
        msgbox_header = browser.get_element(msgbox_header_xpath)
        body_text = browser.get_text(ALCOR_TRANSFERT_URL, body_xpath)
        if body_text and "You are low on CPU! Need more resources?" in body_text:
            # alert(project_name + " " + browser.name + " Alcor sell out of cpu", level=1)
            browser.element_send(browser.get_element(body_xpath), Keys.ESCAPE)
            check_wax_approve(browser)
            return transaction(browser, to, amount, token_send, memo, send_msg)
        if body_text and "Transfer error" in body_text and "duplicate" in body_text:
            return True
        if elapsed_minutes(start) >= 1:
            return transaction(browser, to, amount, token_send, memo, send_msg)
        sleep(0.5)
    transaction_text = get_element_text(msgbox_header)
    if send_msg:
        browser.print(("transaction", to, amount, token_send, memo), False)
        message("{} {} Alcor transaction sent to {} {}".format(amount, token_send, to, memo))
    if not transaction_text or (transaction_text and "Transaction complete!" not in transaction_text):
        # relaunch apres avoir vérifié que tout est correct
        say(name + " check validate Alcor transaction")
        say(name + " check validate Alcor transaction")
        message(name + " check validate Alcor transaction")
        sleep(30)
    return True


def buy(browser: Browser, asset: str, roof_tokens_to_have: float) -> tuple[bool, bool]:
    asset = asset.upper()
    browser.print(("Alcor.buy", asset, roof_tokens_to_have), False)
    if not connect(browser):
        return False, False
    connect_to_trading(browser, asset)
    higher_bid_amount_xpath = "/html/body/div[1]/div/div/div[4]/div/div/div/div[2]/div/div[1]/div[1]/div/div[4]/div[1]"
    if browser.wait_text(alcor_trade_url, higher_bid_amount_xpath) is None:
        return False, False
    devise_amount = search_n_get_float(browser.get_text(alcor_trade_url, devise_xpath))
    token_amount = search_n_get_float(browser.get_text(alcor_trade_url, my_tokens_xpath))
    higher_bid_amount = search_n_get_float(browser.get_text(alcor_trade_url, higher_bid_amount_xpath))
    if higher_bid_amount is None:
        return False, False
    price_input_xpath = "/html/body/div/div/div/div[4]/div/div/div/div[2]/div/div[2]/div[2]/div[1]/div/div[2]/div[2]/div[1]/div/div/div[1]/form/div[1]/div/div/input"
    price_input = browser.get_element(price_input_xpath)
    if token_amount >= roof_tokens_to_have * 0.95:
        browser.print(
            ("Alcor.buy token_amount >= roof_tokens_to_have * 0.95",
             token_amount, roof_tokens_to_have * 0.95), False)
        return True, True
    devise_to_send = (roof_tokens_to_have - token_amount) * higher_bid_amount
    if devise_amount <= devise_to_send:
        # browser.print(("Alcor.buy devise_amount <= devise_to_send", devise_amount, devise_to_send), False)
        browser.print(("Alcor.buy devise_amount <= devise_to_send send all", devise_amount, devise_to_send), False)
        devise_to_send = devise_amount
        # return True, True
    browser.element_send(price_input, higher_bid_amount + 0.0000001)
    browser.print(("devise_to_send", devise_to_send, "use", devise_to_send * higher_bid_amount))
    total_input_xpath = "/html/body/div[1]/div/div/div[4]/div/div/div/div[2]/div/div[2]/div[2]/div[1]/div/div[2]/div[2]/div[1]/div/div/div[1]/form/div[4]/div/div/input"
    total_input = browser.get_element(total_input_xpath)
    browser.clear_send(total_input)
    browser.element_send(total_input, devise_to_send)
    buy_button_xpath = "/html/body/div/div/div/div[4]/div/div/div/div[2]/div/div[2]/div[2]/div[1]/div/div[2]/div[2]/div[1]/div/div/div[1]/form/div[5]/div/button"
    browser.get_element_n_click(buy_button_xpath)
    # laaa
    start = now()
    trades_class = "el-table__row"
    existing_trades = browser.get_element(existing_trades_xpath)
    while existing_trades and len(existing_trades.find_elements_by_class_name(trades_class)) == 0:
        wierd_header_xpath = "/html/body"
        wierd_header_text = browser.get_text(ALCOR_TRANSFERT_URL, wierd_header_xpath)
        if wierd_header_text and "Transfer error" in wierd_header_text and "duplicate" in wierd_header_text:
            return True, False
        if elapsed_seconds(start) > 30:
            return False, False
        sleep(1)
        existing_trades = browser.get_element(existing_trades_xpath)
    return True, False


def sell(browser: Browser, asset: str, floor_tokens_to_keep: float = -1, verif=False) -> tuple[bool, bool]:
    """ reutnr good, finished"""
    project_name = frameinfo(2)["filename"]
    asset = asset.upper()
    ratio_tokens_befor_me_to_cancel = 0.95
    browser.print(("Alcor.sell", asset, floor_tokens_to_keep), False)
    while not connect(browser):
        sleep(2)
    connect_to_trading(browser, asset)
    sell_price = 0
    click = False
    my_tokens_amount = search_n_get_float(browser.get_text(alcor_trade_url, my_tokens_xpath))
    while True:
        existing_trades = browser.get_element(existing_trades_xpath)
        if existing_trades is None:
            return False, False
        trades_class = "el-table__row"
        my_trades = existing_trades.find_elements_by_class_name(trades_class)
        trades_len = len(my_trades)
        if trades_len == 0:
            asks = get_all_asks(browser)
            sum_tokens_befor_me = 0
            for ask in asks:
                ask_text = get_element_text(ask)
                if ask_text is None or ask_text == "":
                    return False, False
                ask_price_devise, token_amount, total_ask_devise = map(lambda x: float(x.replace(",", "")),
                                                                       ask_text.split())
                sum_tokens_befor_me += token_amount
                if sum_tokens_befor_me > my_tokens_amount * ratio_tokens_befor_me_to_cancel:
                    sell_price = ask_price_devise
                    break
            if sell_price > 0:
                break
        elif trades_len > 1:
            browser.get_element_n_click(cancel_all_orders_xpath)
            click = True
            sleep(1)
            continue
        elif trades_len == 1:
            trade = my_trades[0]
            trade_txt = get_element_text(trade)
            my_date_trade, trades_asset, my_type_trade, my_price, total_asset, total_devise, _ = trade_txt.split("\n")
            my_ask, my_bid, my_price = map(lambda x: search_n_get_float(x), (total_asset, total_devise, my_price))
            is_sell = "SELL" == my_type_trade
            if not is_sell:
                browser.get_element_n_click(cancel_all_orders_xpath)
                click = True
                break
            while True:
                asks = get_all_asks(browser)
                sum_tokens_befor_me = 0
                ask_text = None
                out = False
                out_trades_len_1 = False
                for ask in asks:
                    check_existing_trades = existing_trades.find_elements_by_class_name(trades_class)
                    if len(check_existing_trades) == 0:
                        out_trades_len_1 = True
                        break
                    ask_text = get_element_text(ask)
                    start_loop = now()
                    while ask_text is None or ask_text == "":
                        ask_text = get_element_text(ask)
                        if elapsed_seconds(start_loop) >= 5:
                            break
                    if ask_text is None or ask_text == "":
                        break
                    ask_price_devise, token_amount, total_ask_devise = map(lambda x: float(x.replace(",", "")),
                                                                           ask_text.split())
                    is_my_ask = float(my_price) == ask_price_devise
                    if not is_my_ask:
                        sum_tokens_befor_me += token_amount
                    # N'actualise pas le trade lorsque la somme des tokens jusqu'point l'ordre est < à l'ordre
                    elif sum_tokens_befor_me <= my_tokens_amount * ratio_tokens_befor_me_to_cancel:
                        browser.print(
                            ("order_exist_and_is_fine",
                             sum_tokens_befor_me, "<=", my_tokens_amount * ratio_tokens_befor_me_to_cancel))
                        out = True
                        break
                    else:
                        browser.print(
                            ("order_exist_and_is_not_fine_cancel_order",
                             # sum_tokens_befor_me, ">", token_amount * ratio_tokens_befor_me_to_cancel))
                             sum_tokens_befor_me, ">", my_bid * ratio_tokens_befor_me_to_cancel))
                        browser.get_element_n_click(cancel_all_orders_xpath)
                        click = True
                        out = True
                        break
                if out or out_trades_len_1:
                    break
                if ask_text is None or ask_text == "":
                    browser.print("order_exist_and_is_too_high")
                    browser.get_element_n_click(cancel_all_orders_xpath)
                    click = True
                    break
                break
            if out:
                break
    cancel_confirm_xpath = "/html/body/div[3]/div/div[3]/button[2]"
    cancel_confirm = browser.get_element(cancel_confirm_xpath)
    if cancel_confirm:
        browser.element_click(cancel_confirm)
    sleep(2)
    body_xpath = "/html/body"
    body_text = browser.get_text(alcor_trade_url, body_xpath)
    if body_text and "You are low on CPU! Need more resources?" in body_text:
        # alert(project_name + " " + browser.name + " Alcor sell out of cpu", level=1)
        browser.element_send(browser.get_element(body_xpath), Keys.ESCAPE)
        check_wax_approve(browser)
        return sell(browser, asset, floor_tokens_to_keep, verif)
    if click:
        check_wax_approve(browser)
        return sell(browser, asset, floor_tokens_to_keep, verif)
    # lower_ask_amount_xpath = "/html/body/div[1]/div/div/div[4]/div/div/div/div[2]/div/div[1]/div[1]/div/div[2]/div[1]"
    # higher_bid_amount_xpath = "/html/body/div[1]/div/div/div[4]/div/div/div/div[2]/div/div[1]/div[1]/div/div[
    # 4]/div[1]"
    # devise_amount = search_n_get_float(browser.get_text(alcor_trade_url, devise_xpath))
    my_tokens_amount = search_n_get_float(browser.get_text(alcor_trade_url, my_tokens_xpath))
    # lower_ask_amount = search_n_get_float(browser.get_text(alcor_trade_url, lower_ask_amount_xpath))
    # higher_bid_amount = search_n_get_float(browser.get_text(alcor_trade_url, higher_bid_amount_xpath))
    price_input_xpath = "/html/body/div[1]/div/div/div[4]/div/div[2]/div/div[5]/div[2]/div/div[2]/div[1]/div/div/div[2]/form/div[1]/div/div/input"
    price_input = browser.get_element(price_input_xpath)
    browser.element_send(price_input, sell_price - 0.0000001)
    if my_tokens_amount <= 0.001 or my_tokens_amount * 0.95 <= floor_tokens_to_keep:
        return True, True
    if floor_tokens_to_keep < 0:  # all
        browser.print(("tokens_to_sell", my_tokens_amount, "to have devise", my_tokens_amount * sell_price))
        if my_tokens_amount * sell_price < 0.6:
            return True, True
        browser.get_element_n_click(my_tokens_xpath)
    else:
        tokens_to_sell = my_tokens_amount - floor_tokens_to_keep
        if tokens_to_sell * sell_price < 0.6:
            return True, True
        browser.print(("tokens_to_sell", tokens_to_sell, "to have devise", tokens_to_sell * sell_price))
        token_input_xpath = "/html/body/div[1]/div/div/div[4]/div/div[2]/div/div[5]/div[2]/div/div[2]/div[1]/div/div/div[2]/form/div[2]/div/div/input"
        token_input = browser.get_element(token_input_xpath)
        browser.clear_send(token_input)
        browser.element_send(token_input, tokens_to_sell)
    sell_button_xpath = "/html/body/div[1]/div/div/div[4]/div/div[2]/div/div[5]/div[2]/div/div[2]/div[1]/div/div/div[2]/form/div[5]/div/button"
    if verif:
        input()
    browser.get_element_n_click(sell_button_xpath)
    check_wax_approve(browser)
    # laaa
    start = now()
    while existing_trades and len(existing_trades.find_elements_by_class_name(trades_class)) == 0:
        body_text = browser.get_text(alcor_trade_url, body_xpath)
        if body_text and "You are low on CPU! Need more resources?" in body_text:
            # alert(project_name + " " + browser.name + " Alcor sell out of cpu", level=1)
            browser.element_send(browser.get_element(body_xpath), Keys.ESCAPE)
            check_wax_approve(browser)
            return sell(browser, asset, floor_tokens_to_keep, verif)
        if body_text and "Transfer error" in body_text and "duplicate" in body_text:
            return True, False
        if elapsed_seconds(start) > 30:
            return sell(browser, asset, floor_tokens_to_keep, verif)
            # return False, False
        sleep(1)
        existing_trades = browser.get_element(existing_trades_xpath)
    return True, False


def connect_to_trading(browser, asset):
    alcor_markets_url = "https://wax.alcor.exchange/markets"
    browser.new_page(alcor_markets_url)
    wax_filter_xpath = "/html/body/div[1]/div/div/div[4]/div/div[1]/div[1]/label[3]"
    if not browser.wait_element_n_click(alcor_markets_url, wax_filter_xpath, leave=15):
        return connect_to_trading(browser, asset)
    search_token_xpath = "/html/body/div[1]/div/div/div[4]/div/div[1]/div[2]/div/input"
    search_token = browser.get_element(search_token_xpath)
    if search_token is not None:
        browser.element_send(search_token, asset)
    tokens_container_xpath = "/html/body/div[1]/div/div/div[4]/div/div[2]/div/div[3]/table/tbody"
    tokens_container = browser.get_element(tokens_container_xpath)
    if tokens_container is None:
        return False
    tokens_tag = "tr"
    tokens = tokens_container.find_elements_by_tag_name(tokens_tag)
    token = None
    for token in tokens:
        token_text = get_element_text(token)
        if token_text is not None and token_text[:len(asset)] == asset:
            break
    if token is None:
        return False
    browser.element_click(token)
    if not browser.wait_url(alcor_trade_url):
        return False
    browser.wait_text(alcor_trade_url, devise_xpath)
    browser.wait_text(alcor_trade_url, my_tokens_xpath)
    verif_n_connect(browser)
    hide_other_pair_xpath = "/html/body/div[1]/div/div/div[4]/div/div[2]/div/div[4]/div[1]/div/div[2]/div"
    hide_other_pair = browser.get_element(hide_other_pair_xpath)
    hide_other_pair_class = get_element_class(hide_other_pair)
    if hide_other_pair_class == "el-switch":
        browser.element_click(hide_other_pair)
    return True


def get_all_asks(browser):
    all_ask_xpath = "/html/body/div[1]/div/div/div[4]/div/div[2]/div/div[2]/div[2]/div[2]/div[1]/div/div[2]"
    all_ask = browser.get_element(all_ask_xpath)
    ask_line_class = "order-row"
    asks = all_ask.find_elements_by_class_name(ask_line_class)
    while len(asks) == 0:
        asks = all_ask.find_elements_by_class_name(ask_line_class)
        sleep(1)
    return asks
