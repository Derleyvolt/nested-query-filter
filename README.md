# nested-query-filter
A nested query filter that filters data from a specific format table based on an unlimited depth query in JSON format.

Below is a component that generates this query based on the UI hierarchy
![image](https://github.com/Derleyvolt/nested-query-filter/assets/35679266/0fdaa935-734d-4c92-a842-46eec3d268a3)

- Every field are expected be string
- Integer, float, and date fields are normalized to compare properly

- It uses Cerberus for data validation and query format validation  [Cerberus](https://docs.python-cerberus.org/)


### Example of a valid Query:

```
{
    "AND": [
        {
            "operator": "btw",
            "field": "payment_date",
            "value": [
                "2024-06-02",
                "2024-07-15"
            ]
        },
        {
            "operator": "eq",
            "field": "posted",
            "value": [
                "1"
            ]
        },
        {
            "OR": [
                {
                    "operator": "lt",
                    "field": "number",
                    "value": [
                        "200"
                    ]
                },
                {
                    "operator": "sw",
                    "field": "accounts",
                    "value": [
                        "0011"
                    ]
                }
            ]
        }
    ]
}
```
