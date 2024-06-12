from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Product, HomeShopping, BroadcastSchedule
import datetime

class BroadcastProductListView(APIView):

    def get(self, request, *args, **kwargs):
        date = request.GET.get('date')
        site_name_1 = request.GET.get('site_name_1')
        site_name_2 = request.GET.get('site_name_2')
        site_name_3 = request.GET.get('site_name_3')

        if not date or not site_name_1 or not site_name_2 or not site_name_3:
            return Response({"message": "Missing required parameters"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            broadcast_date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return Response({"message": "Invalid date format"}, status=status.HTTP_400_BAD_REQUEST)

        sites = [site_name_1, site_name_2, site_name_3]
        home_shopping_sites = HomeShopping.objects.filter(home_shopping_id__in=sites)

        result_list = []

        for site in home_shopping_sites:
            # BroadcastSchedule에서 날짜와 홈쇼핑사로 필터링
            schedules = BroadcastSchedule.objects.filter(
                broadcast_date=broadcast_date,
                product__home_shopping=site
            )
            product_list = []

            for schedule in schedules:
                product = schedule.product
                now_live_yn = "Y" if schedule.broadcast_time_start <= datetime.datetime.now().time() <= schedule.broadcast_time_end else "N"
                product_data = {
                    "p_id": product.product_id,
                    "p_name": product.product_name,
                    "p_price": f"{product.price:,}원",
                    "live_time": schedule.broadcast_time_start.strftime("%H:%M:%S") if schedule else None,
                    "now_live_yn": now_live_yn,
                    "img_url": product.product_image_url,
                    "p_url": product.product_url,
                    "live_start_time": schedule.broadcast_time_start.strftime("%H:%M:%S") if schedule else None,
                    "live_end_time": schedule.broadcast_time_end.strftime("%H:%M:%S") if schedule else None
                }
                product_list.append(product_data)

            result_list.append({
                "site_name": site.name,
                "products": product_list
            })

        response_data = {
            "message": "success",
            "date": date,
            "list": result_list
        }

        return Response(response_data, status=status.HTTP_200_OK)
