from typing import List, Optional

MessageSections = List[List[str]]

def split_sections(lines: List[str]) -> MessageSections:
    """
    Parses the lines of a message into an array of message sections.
    
    Args:
        lines: The lines of the message.
    
    Returns:
        An array of message sections.
    """
    sections: MessageSections = [[]]
    for line in lines:
        if line == '':
            sections.append([])
        else:
            sections[len(sections) - 1].append(line)
    return sections

def extract_token_domain(sections: MessageSections) -> Optional[str]:
    """
    Extracts the domain from an array of message sections.
    
    Args:
        sections: An array of message sections.
    
    Returns:
        The domain, or None if it cannot be extracted.
    """
    if not sections[0]:
        return None
    last_line = sections[0][-1]
    if last_line.endswith(' wants you to sign in with your Ethereum account.'):
        return last_line.replace(
            ' wants you to sign in with your Ethereum account.', ''
        ).strip()
    return None

def extract_token_statement(sections: MessageSections) -> Optional[str]:
    """
    Extracts the statement from an array of message sections.
    
    Args:
        sections: An array of message sections.
    
    Returns:
        The statement, or None if it cannot be extracted.
    """
    if len(sections) == 2 and not extract_token_domain(sections):
        return sections[0][0]
    if len(sections) == 3:
        return sections[1][0]
    return None 