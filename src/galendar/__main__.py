"""Entry point for calendar app"""

import os
import sys

import dropbox


def main():
    print(" ".join(sys.argv[1:]))
    oauth = auth_with_dropbox()
    with dropbox.Dropbox(oauth2_access_token=oauth.access_token) as dbx:
        name = dbx.users_get_current_account().name.familiar_name
        print(f"Welcome, {name}")

        for file in dbx.files_list_folder("").entries:
            print("*" * 70, "\n", file.name)
            _, response = dbx.files_download(file.path_display)
            print(response.text)
        print("Done")


def auth_with_dropbox():
    """Authorize with Dropbox"""
    auth_flow = dropbox.DropboxOAuth2FlowNoRedirect(
        os.getenv("DROPBOX_CLIENT_KEY"), os.getenv("DROPBOX_CLIENT_SECRET")
    )

    authorize_url = auth_flow.start()
    print(f"1. Go to: {authorize_url}")
    print("2. Click 'Allow' (you might have to log in first).")
    print("3. Copy the authorization code.")
    auth_code = input("Enter the authorization code: ").strip()

    try:
        return auth_flow.finish(auth_code)
    except Exception as err:
        print(f"Authentication error: {err}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
