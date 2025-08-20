from rest_framework.throttling import AnonRateThrottle

class StartSearchBurstAnonRateThrottle(AnonRateThrottle):
    rate = '10/minute'

class StartSearchSustainedAnonRateThrottle(AnonRateThrottle):
    rate = '100/day'

class BulkMatchesBurstAnonRateThrottle(AnonRateThrottle):
    rate = '8/second'

class RandomIdiomAnonRateThrottle(AnonRateThrottle):
    rate = '20/minute'