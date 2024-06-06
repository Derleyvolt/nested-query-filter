# nested-query-filter
A nested query filter that filters data from a specific format table based on an unlimited depth query in Json format.

- Every field are expected be string
- integer, float, and date fields are normalized to compare properly
- the date is expected to have this format: dd/mm/yyyy



### Example of a valid Query:

```
{
    "AND": [
        {
            "field": "age",
            "operator": "btw",
            "value": ['10', '60']
        }, 
        {
            "field": "date",
            "operator": "btw",
            "value": ["01/01/2024", "01/01/2025"]
        },
        {
            "OR": [
                {
                    "field": "name",
                    "operator": "in",
                    "value": ["joao"]
                },
                {
                    "field": "name",
                    "operator": "eq",
                    "value": ["maria"]
                },
                {
                    "OR": [
                        {
                            "field": "name",
                            "operator": "nin",
                            "value": ["costa"]
                        },
                        {
                            "field": "date",
                            "operator": "lte",
                            "value": ["06/06/2025"]
                        }
                    ]
                }
            ]
        }
    ],
    "OR": [
        {
            "AND": [
                {
                    "field": "age",
                    "operator": "lte",
                    "value": ['71']
                },
                {
                    "field": "name",
                    "operator": "sw",
                    "value": ["ma"]
                },
                {
                    "field": "name",
                    "operator": "ew",
                    "value": ["silva"]
                }
            ]
        },
        {
            {
                "field": "height",
                "operator": "lte",
                "value": ['1.78']
            }
        }
    ]
}
```
