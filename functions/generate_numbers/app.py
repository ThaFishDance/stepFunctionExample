def lambda_handler(event, context):
    print(event)
    print(context)
    # event will contain { "name1": ..., "name2": ... }
    return {
        "numbers": list(range(10))
    }
