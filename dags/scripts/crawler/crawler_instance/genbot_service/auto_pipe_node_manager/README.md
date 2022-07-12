m_request = [
    {
        "pipeline": [
            {
                "command": "load_url_static",
                "return_collection_type": "list",
                "url": "https://www.bbc.com/news",
                "data":
                    {
                        "name": "html"
                    }

            },
            {
                "command": "parse_html",
                "return_collection_type": "list",
                "parsable_tags": [
                    "html"
                ],
                "data": [
                    {
                        "validator": "^(?:http(s)?://)?[\\w.-]+(?:\\.[\\w\\.-]+)+[\\w\\-\\._~:/?#[\\]@!\\$&'\\(\\)\\*\\+,;=.]+$",
                        "name": "m_url",
                        "filter": [{
                            "filter_name": "class",
                            "value": "gs-c-promo-heading gs-o-faux-block-link__overlay-link gel-pica-bold nw-o-link-split__anchor",
                            "content": "href", "type": "property","tag":"a"
                        }]
                    }
                ]
            },
            {
                "command": "load_url",
                "return_collection_type": "list",
                "parsable_tags": [
                    "m_url"
                ],
                "data":
                    {
                        "name": "html"
                    }
            },
            {
                "command": "parse_html",
                "return_collection_type": "group",
                "parsable_tags": [
                    "html"
                ],
                "data": [

                    {
                        "validator": "",
                        "name": "date",
                        "filter": [{
                            "filter_name": "class", "value": "ssrcss-1if1g9v-MetadataText ecn1o5v1",
                            "content": "text", "type": "property","tag":"span"
                        }]
                    },
                    {
                        "validator": "",
                        "name": "images",
                        "filter": [{
                            "filter_name": "class", "value": "ssrcss-evoj7m-Image ee0ct7c0",
                            "content": "text", "type": "property","tag":"img"
                        }]
                    },
                    {
                        "validator": "",
                        "name": "m_title",
                        "filter": [{
                            "filter_name": "title", "value": "", "content": "text", "type": "tag","tag":"title"
                        }]
                    },
                    {
                        "validator": "",
                        "name": "m_text",
                        "filter": [{
                            "filter_name": "class", "value": "ssrcss-1q0x1qg-Paragraph eq5iqo00",
                            "content": "text", "type": "property","tag":"p"
                        }]
                    },
                    {
                        "validator": "",
                        "name": "sub_title",
                        "filter": [{
                            "filter_name": "class", "value": "ssrcss-15xko80-StyledHeading e1fj1fc10",
                            "content": "text", "type": "property","tag":"h1"
                        }]
                    }
                ]
            }
        ]
    }
]






pileline : Seperate Rules for Seperate Websites

command : 
   load_url_static : Load Given URL
   load_url : Load Passed URL In Data Object
   parse_html : Parse HTML By Rules

return_collection_type : 
     pass : Return Original URL
     List : Return Data Objects Seperately As List
     Group : Return Data Object As Single Group

data : 
     validator : Validate Final Data By Regex Passed
     name : Set Name Of Returned Object
     filter : Root Path For HTML Variable