import json

from app.models.package import Package


def render_template(package: Package) -> str:
    """
    Create JSON content for the simple API.
    """
    data = {}
    data["name"] = package.name
    data["meta"]["api-version"] = "1.0"
    # we return 1.0 and not 1.1 because we do not support the version list
    # added in 1.1
    data["meta"]["_last-updated"] = package.last_updated.isoformat()

    # add files
    data["files"] = []
    for code_file in package.code_files:
        # required fields
        file_data = {
            "filename": code_file.filename,
            "url": code_file.download_url,
            "hashes": code_file.hashes_dict,
        }

        # optional fields
        if code_file.requires_python:
            file_data["requires-python"] = code_file.requires_python

        if code_file.yanked:
            file_data["yanked"] = code_file.yanked

        if code_file.metadata_file:
            # default to True
            value = True

            # if we have hashes, use them
            if code_file.metadata_file.hashes:
                value = code_file.metadata_file.hashes_dict

            file_data["core-metadata"] = value

            # backwards compatibility
            file_data["dist-info-metadata"] = value

        # append it
        data["files"].append(file_data)

    return json.dumps(data, indent=4)
