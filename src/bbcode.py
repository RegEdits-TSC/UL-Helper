import re
import html
import urllib.parse

class BBCODE:
    def __init__(self):
        pass

    def clean_ptp_description(self, desc, is_disc):
        """
        Clean and format the provided description by removing unwanted tags and links,
        and handling various special cases based on the type of disc.

        Parameters:
        - desc (str): The description text to be cleaned.
        - is_disc (str): The type of disc, used to determine special processing rules.

        Returns:
        - str: The cleaned description.
        """
        
        # Replace bullet points with dashes
        desc = desc.replace("&bull;", "-")

        # Unescape HTML entities
        desc = html.unescape(desc)

        # Normalize line endings
        desc = desc.replace('\r\n', '\n')

        # Remove PTP/HDB URL tags and replace them with a simple format
        url_patterns = [
            r"\[url[\=\]]https?:\/\/passthepopcorn\.m[^\]]+\[\/url\]?",
            r"\[url[\=\]]https?:\/\/hdbits\.o[^\]]+\[\/url\]?"
        ]
        for pattern in url_patterns:
            desc = re.sub(pattern, "", desc, flags=re.IGNORECASE)

        # Replace specific URLs with simplified text
        desc = desc.replace('http://passthepopcorn.me', 'PTP').replace('https://passthepopcorn.me', 'PTP')
        desc = desc.replace('http://hdbits.org', 'HDB').replace('https://hdbits.org', 'HDB')

        # Remove Mediainfo tags and specific mediainfo content based on the disc type
        if is_disc != "BDMV":
            desc = re.sub(r"\[mediainfo\][\s\S]*?\[\/mediainfo\]", "", desc)
            # Regex to remove mediainfo sections or specific content
            desc = re.sub(r"(^general\nunique)(.*?)^$", "", desc, flags=re.MULTILINE | re.IGNORECASE | re.DOTALL)
            desc = re.sub(r"(^general\ncomplete)(.*?)^$", "", desc, flags=re.MULTILINE | re.IGNORECASE | re.DOTALL)
            desc = re.sub(r"(^(Format[\s]{2,}:))(.*?)^$", "", desc, flags=re.MULTILINE | re.IGNORECASE | re.DOTALL)
            desc = re.sub(r"(^(video|audio|text)( #\d+)?\nid)(.*?)^$", "", desc, flags=re.MULTILINE | re.IGNORECASE | re.DOTALL)
            desc = re.sub(r"(^(menu)( #\d+)?\n)(.*?)^$", "", f"{desc}\n\n", flags=re.MULTILINE | re.IGNORECASE | re.DOTALL)
        elif any(x in is_disc for x in ["BDMV", "DVD"]):
            # Return empty string for specific disc types
            return ""

        # Convert Quote tags to Code tags
        desc = re.sub(r"\[quote.*?\]", "[code]", desc)
        desc = desc.replace("[/quote]", "[/code]")

        # Remove alignment and size tags
        desc = re.sub(r"\[align=.*?\]", "", desc)
        desc = desc.replace("[/align]", "")
        desc = re.sub(r"\[size=.*?\]", "", desc)
        desc = desc.replace("[/size]", "")

        # Remove video and staff tags
        desc = re.sub(r"\[video\][\s\S]*?\[\/video\]", "", desc)
        desc = re.sub(r"\[staff[\s\S]*?\[\/staff\]", "", desc)

        # Remove various other tags and elements
        remove_list = [
            '[movie]', '[/movie]',
            '[artist]', '[/artist]',
            '[user]', '[/user]',
            '[indent]', '[/indent]',
            '[size]', '[/size]',
            '[hr]'
        ]
        for tag in remove_list:
            desc = desc.replace(tag, '')

        # Replace comparison and hide tags with placeholders
        comps = re.findall(r"\[comparison=[\s\S]*?\[\/comparison\]", desc)
        hides = re.findall(r"\[hide[\s\S]*?\[\/hide\]", desc)
        comps.extend(hides)

        comp_placeholders = []
        for i, comp in enumerate(comps):
            desc = desc.replace(comp, f"COMPARISON_PLACEHOLDER-{i} ")
            comp_placeholders.append(comp)

        # Remove IMG tags and replace loose images with nothing
        desc = re.sub(r"\[img\][\s\S]*?\[\/img\]", "", desc, flags=re.IGNORECASE)
        desc = re.sub(r"\[img=[\s\S]*?\]", "", desc, flags=re.IGNORECASE)

        # Remove loose image URLs
        loose_images = re.findall(r"(https?:\/\/.*\.(?:png|jpg))", desc, flags=re.IGNORECASE)
        for image in loose_images:
            desc = desc.replace(image, '')

        # Restore placeholders with original content
        for i, comp in enumerate(comp_placeholders):
            comp = re.sub(r"\[\/?img[\s\S]*?\]", "", comp, flags=re.IGNORECASE)
            desc = desc.replace(f"COMPARISON_PLACEHOLDER-{i} ", comp)

        # Convert hides with multiple images to comparisons
        desc = self.convert_collapse_to_comparison(desc, "hide", hides)

        # Clean up blank lines
        desc = desc.strip('\n')
        desc = re.sub(r"\n\n+", "\n\n", desc)
        while desc.startswith('\n'):
            desc = desc.replace('\n', '', 1)
        desc = desc.strip('\n')

        return "" if desc.replace('\n', '') == '' else desc

    def convert_collapse_to_comparison(self, desc, tag_type, tags):
        """
        Placeholder method for converting collapsible content to comparisons.

        Parameters:
        - desc (str): The description text to be cleaned.
        - tag_type (str): The type of tag to convert.
        - tags (list): List of tags to be converted.

        Returns:
        - str: The updated description.
        """
        # Placeholder implementation (to be replaced with actual logic)
        return desc
    
    def clean_unit3d_description(self, desc, site):
        """
        Clean and format the provided description by removing or converting various BBCode tags, 
        handling special cases like spoilers and images, and cleaning up unwanted elements.

        Parameters:
        - desc (str): The description text to be cleaned.
        - site (str): The base URL of the site to remove from the description.

        Returns:
        - tuple: A tuple containing:
            - str: The cleaned description.
            - list: A list of image information dictionaries.
        """
        
        # Unescape HTML entities and normalize newlines
        desc = html.unescape(desc).replace('\r\n', '\n')

        # Remove links to the specified site
        site_netloc = urllib.parse.urlparse(site).netloc
        site_regex = rf"\[url[\=\]]https?:\/\/{site_netloc}/[^\]]+(\[\/url\])?"
        desc = re.sub(site_regex, '', desc, flags=re.IGNORECASE)

        # Replace site domain with its first part
        desc = desc.replace(site_netloc, site_netloc.split('.')[0])

        # Temporarily hide spoiler tags by replacing them with placeholders
        spoilers = re.findall(r"\[spoiler[\s\S]*?\[\/spoiler\]", desc)
        spoiler_placeholders = []
        for i, spoiler in enumerate(spoilers):
            placeholder = f"SPOILER_PLACEHOLDER-{i} "
            desc = desc.replace(spoiler, placeholder)
            spoiler_placeholders.append(spoiler)

        # Extract and remove images from URL tags
        imagelist = []
        url_tags = re.findall(r"\[url=[\s\S]*?\[\/url\]", desc)
        for tag in url_tags:
            images = re.findall(r"\[img[\s\S]*?\[\/img\]", tag)
            if len(images) == 1:
                img_url = re.sub(r"\[img[\s\S]*?\]", "", images[0]).lower()
                web_url = re.match(r"\[url=[\s\S]*?\]", tag, flags=re.IGNORECASE)
                if web_url:
                    web_url = re.sub(r"\[url=|\]$", "", web_url.group()).lower()
                image_dict = {
                    'img_url': img_url,
                    'raw_url': img_url,
                    'web_url': web_url
                }
                imagelist.append(image_dict)
                desc = desc.replace(tag, '')

        # Remove bot signatures and specific unwanted elements
        desc = re.sub(
            r"\[img=35]https://blutopia/favicon.ico[/img] [b]Uploaded Using [url=https://github.com/HDInnovations/UNIT3D]UNIT3D[/url] Auto Uploader[/b] [img=35]https://blutopia/favicon.ico[/img]",
            '', desc)
        desc = re.sub(r"\[center\].*Created by L4G's Upload Assistant.*\[\/center\]", '', desc, flags=re.IGNORECASE)

        # Restore spoiler tags from placeholders
        for i, placeholder in enumerate(spoiler_placeholders):
            desc = desc.replace(f"SPOILER_PLACEHOLDER-{i} ", placeholder)

        # Clean up empty [center] tags
        centers = re.findall(r"\[center[\s\S]*?\[\/center\]", desc)
        for center in centers:
            clean_center = re.sub(r'\[center\]|\s|\n|\[\/center\]', '', center)
            if not clean_center:
                desc = desc.replace(center, '')

        # Convert comparison spoilers to [comparison=]
        desc = self.convert_collapse_to_comparison(desc, "spoiler", spoilers)

        # Clean up extra blank lines
        desc = re.sub(r'\n+', '\n', desc.strip())

        return desc if desc.strip() else "", imagelist

    def convert_collapse_to_comparison(self, desc, tag_type, tags):
        """
        Placeholder method for converting collapsible content to comparisons.

        Parameters:
        - desc (str): The description text to be cleaned.
        - tag_type (str): The type of tag to convert.
        - tags (list): List of tags to be converted.

        Returns:
        - str: The updated description.
        """
        # Placeholder implementation (to be replaced with actual logic)
        return desc
    
    def convert_pre_to_code(self, desc):
        """
        Convert [pre] tags to [code] tags in the description.
        """
        return desc.replace('[pre]', '[code]').replace('[/pre]', '[/code]')

    def convert_hide_to_spoiler(self, desc):
        """
        Convert [hide] tags to [spoiler] tags in the description.
        """
        return desc.replace('[hide', '[spoiler').replace('[/hide]', '[/spoiler]')

    def convert_spoiler_to_hide(self, desc):
        """
        Convert [spoiler] tags to [hide] tags in the description.
        """
        return desc.replace('[spoiler', '[hide').replace('[/spoiler]', '[/hide]')

    def remove_spoiler(self, desc):
        """
        Remove all [spoiler] tags and their contents from the description.
        """
        return re.sub(r"\[\/?spoiler[\s\S]*?\]", "", desc, flags=re.IGNORECASE)

    def convert_spoiler_to_code(self, desc):
        """
        Convert [spoiler] tags to [code] tags in the description.
        """
        return desc.replace('[spoiler', '[code').replace('[/spoiler]', '[/code]')

    def convert_code_to_quote(self, desc):
        """
        Convert [code] tags to [quote] tags in the description.
        """
        return desc.replace('[code', '[quote').replace('[/code]', '[/quote]')

    def convert_comparison_to_collapse(self, desc, max_width):
        """
        Convert [comparison] tags to [spoiler] tags with image links and resized images.

        Args:
            desc (str): The description containing the BBCode to be converted.
            max_width (int): The maximum width for resizing images.

        Returns:
            str: The converted description.
        """
        comparisons = re.findall(r"\[comparison=[\s\S]*?\[\/comparison\]", desc)
        for comp in comparisons:
            # Extract sources and images from the comparison tag
            comp_sources = comp.split(']', 1)[0].replace('[comparison=', '').replace(' ', '').split(',')
            comp_images = re.findall(r"(https?:\/\/.*\.(?:png|jpg))", comp.split(']', 1)[1], flags=re.IGNORECASE)
            screens_per_line = len(comp_sources)
            
            # Determine image size
            img_size = min(int(max_width / screens_per_line), 350)
            
            # Build the new BBCode for the comparison
            line = []
            output = []
            for img in comp_images:
                img = img.strip()
                if img:
                    line.append(f"[url={img}][img={img_size}]{img}[/img][/url]")
                    if len(line) == screens_per_line:
                        output.append(''.join(line))
                        line = []
            output = '\n'.join(output)
            new_bbcode = (f"[spoiler={' vs '.join(comp_sources)}]"
                          f"[center]{' | '.join(comp_sources)}[/center]\n"
                          f"{output}[/spoiler]")
            desc = desc.replace(comp, new_bbcode)
        return desc

    def convert_comparison_to_centered(self, desc, max_width):
        """
        Convert [comparison] tags to [center] tags with image links and resized images.

        Args:
            desc (str): The description containing the BBCode to be converted.
            max_width (int): The maximum width for resizing images.

        Returns:
            str: The converted description.
        """
        comparisons = re.findall(r"\[comparison=[\s\S]*?\[\/comparison\]", desc)
        for comp in comparisons:
            # Extract sources and images from the comparison tag
            comp_sources = comp.split(']', 1)[0].replace('[comparison=', '').replace(' ', '').split(',')
            comp_images = re.findall(r"(https?:\/\/.*\.(?:png|jpg))", comp.split(']', 1)[1], flags=re.IGNORECASE)
            screens_per_line = len(comp_sources)
            
            # Determine image size
            img_size = min(int(max_width / screens_per_line), 350)
            
            # Build the new BBCode for the comparison
            line = []
            output = []
            for img in comp_images:
                img = img.strip()
                if img:
                    bb = f"[url={img}][img={img_size}]{img}[/img][/url]"
                    line.append(bb)
                    if len(line) == screens_per_line:
                        output.append(''.join(line))
                        line = []
            output = '\n'.join(output)
            new_bbcode = f"[center]{' | '.join(comp_sources)}\n{output}[/center]"
            desc = desc.replace(comp, new_bbcode)
        return desc
    
    def convert_collapse_to_comparison(self, desc, spoiler_hide, collapses):
        """
        Convert spoiler/hide tags with multiple images to [comparison] tags.

        Args:
            desc (str): The description containing the BBCode to be converted.
            spoiler_hide (str): The type of collapse tag ('spoiler' or 'hide').
            collapses (list): List of collapse tags to be converted.

        Returns:
            str: The converted description.
        """
        if collapses:
            for tag in collapses:
                # Find all image tags within the collapse tag
                images = re.findall(r"\[img[\s\S]*?\[\/img\]", tag, flags=re.IGNORECASE)
                
                # Only convert if there are 6 or more images
                if len(images) >= 6:
                    comp_images = []
                    final_sources = []

                    # Extract image URLs
                    for image in images:
                        image_url = re.sub(r"\[img[\s\S]*\]", "", image.replace('[/img]', ''), flags=re.IGNORECASE)
                        comp_images.append(image_url)

                    # Extract and clean sources
                    if spoiler_hide == "spoiler":
                        sources = re.match(r"\[spoiler[\s\S]*?\]", tag)[0].replace('[spoiler=', '')[:-1]
                    elif spoiler_hide == "hide":
                        sources = re.match(r"\[hide[\s\S]*?\]", tag)[0].replace('[hide=', '')[:-1]
                    sources = re.sub(r"comparison", "", sources, flags=re.IGNORECASE)
                    for delimiter in ['vs', ',', '|']:
                        sources = sources.split(delimiter)
                        sources = "$".join(sources)
                    sources = sources.split("$")
                    for source in sources:
                        final_sources.append(source.strip())

                    # Build the new [comparison] tag
                    comp_images = '\n'.join(comp_images)
                    final_sources = ', '.join(final_sources)
                    spoil2comp = f"[comparison={final_sources}]{comp_images}[/comparison]"
                    desc = desc.replace(tag, spoil2comp)
        return desc