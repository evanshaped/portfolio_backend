from rest_framework.throttling import AnonRateThrottle

class StartSearchBurstAnonRateThrottle(AnonRateThrottle):
    rate = '2/minute'

class StartSearchSustainedAnonRateThrottle(AnonRateThrottle):
    rate = '20/day'

class BulkMatchesBurstAnonRateThrottle(AnonRateThrottle):
    rate = '4/second'

class RandomIdiomAnonRateThrottle(AnonRateThrottle):
    rate = '2/minute'