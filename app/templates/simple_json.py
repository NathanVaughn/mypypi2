import json

from app.constants import METADATA_KEY, METADATA_KEY_LEGACY, METADATA_KEY_LEGACY2
from app.models.package import Package


def render_template(package: Package) -> str:
    """
    Create JSON content for the simple API.
    """
    data = {}
    # add name key
    data["name"] = package.name
    # add version key
    data["version"] = package.versions
    # add meta key
    data["meta"] = {}
    data["meta"]["api-version"] = "1.4"
    data["meta"]["tracks"] = [package.repository_url]
    # we return 1.0 and not 1.1 because we do not support the version list
    # added in 1.1
    # https://packaging.python.org/en/latest/specifications/simple-repository-api/#additional-fields-for-the-simple-api-for-package-indexes
    # we only can grab data from the HTML api reliabily, so this does not contain
    # all the fields needed to return a 1.1 response.
    data["meta"]["_last-updated"] = package.last_updated.isoformat()

    # add status if available
    data["project-status"] = {}
    if package.status:
        data["project-status"]["status"] = package.status
    if package.status_reason:
        data["project-status"]["reason"] = package.status_reason

    # add files
    data["files"] = []
    for code_file in package.code_files:
        # required fields
        file_data = {
            "filename": code_file.filename,
            "url": code_file.download_url,
            "hashes": code_file.hashes_dict,
            "provenance": code_file.provenance,
        }

        # optional fields
        if code_file.requires_python:
            file_data["requires-python"] = code_file.requires_python

        if code_file.size is not None:
            file_data["size"] = code_file.size

        if code_file.upload_time:
            file_data["upload-time"] = code_file.upload_time.isoformat()

        # yanked can be a boolean or a reason
        file_data["yanked"] = code_file.yanked

        if code_file.metadata_file:
            # default to True
            value = True

            # if we have hashes, use them
            if code_file.metadata_file.hashes:
                value = code_file.metadata_file.hashes_dict

            file_data[METADATA_KEY] = value

            # backwards compatibility
            file_data[METADATA_KEY_LEGACY] = value

            # be like pypi
            file_data[METADATA_KEY_LEGACY2] = value

        # append it
        data["files"].append(file_data)

    return json.dumps(data, indent=4)
