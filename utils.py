def number_to_words(num):
    """Convert a number to words representation"""
    units = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
    tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']

    def _convert_less_than_thousand(num):
        if num < 20:
            return units[num]
        elif num < 100:
            return tens[num // 10] + ('' if num % 10 == 0 else ' ' + units[num % 10])
        else:
            return units[num // 100] + ' Hundred' + ('' if num % 100 == 0 else ' and ' + _convert_less_than_thousand(num % 100))

    if num == 0:
        return 'Rupees Zero Only'

    # Handle decimal part
    rupees = int(num)
    paise = int(round((num - rupees) * 100))

    result = 'Rupees '
    crore = rupees // 10000000
    rupees %= 10000000
    lakh = rupees // 100000
    rupees %= 100000
    thousand = rupees // 1000
    rupees %= 1000

    if crore:
        result += _convert_less_than_thousand(crore) + ' Crore '
    if lakh:
        result += _convert_less_than_thousand(lakh) + ' Lakh '
    if thousand:
        result += _convert_less_than_thousand(thousand) + ' Thousand '
    if rupees:
        result += _convert_less_than_thousand(rupees)

    if paise:
        result += ' and ' + _convert_less_than_thousand(paise) + ' Paise'

    return result.strip() + ' Only'
