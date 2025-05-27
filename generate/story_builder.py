def build_storyboard(scenes: list, generation_function) -> list:
    """
    Takes a list of (scene_title, scene_summary) tuples and a function
    to generate full output (narration + visuals) for each scene.
    
    Returns a list of structured scene dictionaries.
    """

    storyboard = []

    for i, (scene_title, scene_summary) in enumerate(scenes, 1):
        scene_output = generation_function(scene_title, scene_summary)

        storyboard.append({
            "scene_number": i,
            "scene_title": scene_title,
            "summary": scene_summary,
            "full_output": scene_output.strip()
        })

    return storyboard
