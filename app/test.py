import re

def parse_char_list_to_urls(self=None, char_list=None):
    if char_list is None:
        char_list = self.image_url

    if not char_list:
        return []

    # Step 1: Remove all junk commas
    chars_only = [c for c in char_list if c != ',']

    # Step 2: Rebuild the string
    full_str = ''.join(chars_only)

    # Step 3: Strip outer {}
    if full_str.startswith('{') and full_str.endswith('}'):
        full_str = full_str[1:-1]

    # Step 4: Insert comma before every http/https after the first one
    full_str = re.sub(r'(https?:\/\/)', r',\1', full_str, count=0)

    # Step 5: Split on commas
    urls = [url.strip() for url in full_str.split(',') if url.strip()]

    return urls
