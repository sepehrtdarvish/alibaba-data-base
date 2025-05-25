from users.models import UserAccount
from organisation.models import Company
from organisation.exceptions import CompanyNotFoundException

def company_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        company = Company.objects.filter(owner=request.user).first()
        if not company:
            raise CompanyNotFoundException()
        request.company = company
        return view_func(request, *args, **kwargs)

    return _wrapped_view
