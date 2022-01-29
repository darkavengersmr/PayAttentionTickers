#!/usr/bin/python3

# asyncPayAttentionTickers

import async_api
import config

def main():
    config.make_paths()
    async_api.api_daemon()

if __name__ == '__main__':
    main()







