import random
from datetime import datetime
from app.models.literature import Literature
from app.db.session import get_db
from sqlalchemy.future import select
from fastapi import Depends, status, Query
from fastapi.responses import JSONResponse
from app.utils.language import get_language
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.schemas.literature import CreateLiterature, UpdateLiterature
from app.utils.translator import translate_to_english
from app.models.translation.literature_translation import LiteratureTrans
from sqlalchemy import func, and_, or_
import traceback

class LiteratureCRUD:
    
    def generate_literature_code(self):
        """Literature code yaradır"""
        random_number = random.randint(10000, 99999)
        return random_number

    async def add_literature(
        self,
        literature_request: CreateLiterature,
        db: AsyncSession
    ):
        """Yeni literature tərcümələri ilə birlikdə yaradır"""
        try:
            # Literature code-un unikallığını yoxla
            existing_query = await db.execute(
                select(Literature)
                .where(Literature.literature_code == literature_request.literature_code)
            )
            
            existing_literature = existing_query.scalars().first()
            
            if existing_literature:
                return JSONResponse(
                    content={
                        "statusCode": 400,
                        "message": f"Literature with code {literature_request.literature_code} already exists"
                    }, status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Yeni literature yarad
            new_literature = Literature(
                literature_code=literature_request.literature_code,
                specialty_code=literature_request.specialty_code,
                url=literature_request.url,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            # Azərbaycan dilində tərcümə
            new_literature_az = LiteratureTrans(
                literature_code=literature_request.literature_code,
                language_code="az",
                literature_name=literature_request.literature_name,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            # İngilis dilinə tərcümə
            new_literature_en = LiteratureTrans(
                literature_code=literature_request.literature_code,
                language_code="en",
                literature_name=translate_to_english(literature_request.literature_name),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            db.add(new_literature)
            db.add(new_literature_az)
            db.add(new_literature_en)
            
            await db.commit()
            await db.refresh(new_literature)
            await db.refresh(new_literature_az)
            await db.refresh(new_literature_en)

            return JSONResponse(
                content={
                    "statusCode": 201,
                    "message": "Literature created successfully."
                }, status_code=status.HTTP_201_CREATED
            )

        except Exception as e:
            print("Add literature error:", e)
            traceback.print_exc()
            return JSONResponse(
                content={
                    "statusCode": 500,
                    "error": str(e)
                }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    async def get_literature_by_specialty_code(
        self,
        specialty_code: int,
        start: int,
        end: int,
        lang_code: str,
        db: AsyncSession
    ):
        """Specialty code-a görə literature-ləri gətirir"""
        try:
            # Total sayını hesabla
            total_query = await db.execute(
                select(func.count()).select_from(Literature).where(Literature.specialty_code == specialty_code)
            )
            total = total_query.scalar()

            if total == 0:
                return JSONResponse(
                    content={
                        "statusCode": 204,
                        "message": "No content"
                    }, status_code=status.HTTP_200_OK
                )

            literature_arr = []

            # Literature-ləri gətir
            literature_query = await db.execute(
                select(Literature)
                .where(Literature.specialty_code == specialty_code)
                .offset(start)
                .limit(end - start)
            )

            literatures = literature_query.scalars().all()

            for literature in literatures:
                # Tərcümələri gətir
                literature_translations_query = await db.execute(
                    select(LiteratureTrans)
                    .where(
                        and_(
                            LiteratureTrans.literature_code == literature.literature_code,
                            LiteratureTrans.language_code == lang_code
                        )
                    )
                )

                literature_translations = literature_translations_query.scalar_one_or_none()

                literature_obj = {
                    "id": literature.id,
                    "literature_code": literature.literature_code,
                    "specialty_code": literature.specialty_code,
                    "literature_name": literature_translations.literature_name if literature_translations else None,
                    "url": literature.url,
                    "created_at": literature.created_at.isoformat() if literature.created_at else None,
                    "updated_at": literature.updated_at.isoformat() if literature.updated_at else None
                }

                literature_arr.append(literature_obj)
            
            return JSONResponse(
                content={
                    "statusCode": 200,
                    "literatures": literature_arr,
                    "total": total
                }
            )
        
        except Exception as e:
            print("Get literature by specialty error:", e)
            traceback.print_exc()
            return JSONResponse(
                content={
                    "statusCode": 500,
                    "error": str(e)
                }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    async def get_literature_by_code(
        self,
        literature_code: int,
        lang_code: str,
        db: AsyncSession
    ):
        """Literature code-a görə tək literature gətirir"""
        try:
            # Literature tap
            literature_query = await db.execute(
                select(Literature)
                .where(Literature.literature_code == literature_code)
            )
            
            literature = literature_query.scalars().first()
            
            if not literature:
                return JSONResponse(
                    content={
                        "statusCode": 404,
                        "message": "Literature not found"
                    }, status_code=status.HTTP_404_NOT_FOUND
                )

            # Tərcümə gətir
            literature_translations_query = await db.execute(
                select(LiteratureTrans)
                .where(
                    and_(
                        LiteratureTrans.literature_code == literature_code,
                        LiteratureTrans.language_code == lang_code
                    )
                )
            )

            literature_translations = literature_translations_query.scalar_one_or_none()

            literature_obj = {
                "id": literature.id,
                "literature_code": literature.literature_code,
                "specialty_code": literature.specialty_code,
                "literature_name": literature_translations.literature_name if literature_translations else None,
                "url": literature.url,
                "created_at": literature.created_at.isoformat() if literature.created_at else None,
                "updated_at": literature.updated_at.isoformat() if literature.updated_at else None
            }

            return JSONResponse(
                content={
                    "statusCode": 200,
                    "literature": literature_obj
                }
            )
        
        except Exception as e:
            print("Get literature by code error:", e)
            traceback.print_exc()
            return JSONResponse(
                content={
                    "statusCode": 500,
                    "error": str(e)
                }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    async def get_all_literatures(
        self,
        start: int,
        end: int,
        lang_code: str,
        db: AsyncSession
    ):
        """Bütün literature-ləri gətirir"""
        try:
            # Total sayını hesabla
            total_query = await db.execute(
                select(func.count()).select_from(Literature)
            )
            total = total_query.scalar()

            if total == 0:
                return JSONResponse(
                    content={
                        "statusCode": 204,
                        "message": "No content"
                    }, status_code=status.HTTP_200_OK
                )

            literature_arr = []

            # Literature-ləri gətir
            literature_query = await db.execute(
                select(Literature)
                .offset(start)
                .limit(end - start)
            )

            literatures = literature_query.scalars().all()

            for literature in literatures:
                # Tərcümələri gətir
                literature_translations_query = await db.execute(
                    select(LiteratureTrans)
                    .where(
                        and_(
                            LiteratureTrans.literature_code == literature.literature_code,
                            LiteratureTrans.language_code == lang_code
                        )
                    )
                )

                literature_translations = literature_translations_query.scalar_one_or_none()

                literature_obj = {
                    "id": literature.id,
                    "literature_code": literature.literature_code,
                    "specialty_code": literature.specialty_code,
                    "literature_name": literature_translations.literature_name if literature_translations else None,
                    "url": literature.url,
                    "created_at": literature.created_at.isoformat() if literature.created_at else None,
                    "updated_at": literature.updated_at.isoformat() if literature.updated_at else None
                }

                literature_arr.append(literature_obj)
            
            return JSONResponse(
                content={
                    "statusCode": 200,
                    "literatures": literature_arr,
                    "total": total
                }
            )
        
        except Exception as e:
            print("Get all literatures error:", e)
            traceback.print_exc()
            return JSONResponse(
                content={
                    "statusCode": 500,
                    "error": str(e)
                }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    async def update_literature(
        self,
        literature_code: int,
        literature_request: UpdateLiterature,
        db: AsyncSession
    ):
        """Literature-i tərcümələri ilə birlikdə yeniləyir"""
        try:
            # Literature tap
            literature_query = await db.execute(
                select(Literature)
                .where(Literature.literature_code == literature_code)
            )
            
            literature = literature_query.scalars().first()
            
            if not literature:
                return JSONResponse(
                    content={
                        "statusCode": 404,
                        "message": "Literature not found"
                    }, status_code=status.HTTP_404_NOT_FOUND
                )

            # Literature məlumatlarını yenilə
            if literature_request.specialty_code is not None:
                literature.specialty_code = literature_request.specialty_code
            if literature_request.url is not None:
                literature.url = literature_request.url
            
            literature.updated_at = datetime.utcnow()

            # Tərcümələri yenilə
            if literature_request.literature_name is not None:
                # Azərbaycan dilində tərcüməni yenilə
                az_trans_query = await db.execute(
                    select(LiteratureTrans)
                    .where(
                        and_(
                            LiteratureTrans.literature_code == literature_code,
                            LiteratureTrans.language_code == "az"
                        )
                    )
                )
                
                az_trans = az_trans_query.scalar_one_or_none()
                
                if az_trans:
                    az_trans.literature_name = literature_request.literature_name
                    az_trans.updated_at = datetime.utcnow()

                # İngilis dilində tərcüməni yenilə
                en_trans_query = await db.execute(
                    select(LiteratureTrans)
                    .where(
                        and_(
                            LiteratureTrans.literature_code == literature_code,
                            LiteratureTrans.language_code == "en"
                        )
                    )
                )
                
                en_trans = en_trans_query.scalar_one_or_none()
                
                if en_trans:
                    en_trans.literature_name = translate_to_english(literature_request.literature_name)
                    en_trans.updated_at = datetime.utcnow()

            await db.commit()

            return JSONResponse(
                content={
                    "statusCode": 200,
                    "message": "Literature updated successfully."
                }
            )

        except Exception as e:
            print("Update literature error:", e)
            traceback.print_exc()
            return JSONResponse(
                content={
                    "statusCode": 500,
                    "error": str(e)
                }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    async def delete_literature(
        self,
        literature_code: int,
        db: AsyncSession
    ):
        """Literature-i bütün tərcümələri ilə birlikdə silir"""
        try:
            # Literature tap
            literature_query = await db.execute(
                select(Literature)
                .where(Literature.literature_code == literature_code)
            )
            
            literature = literature_query.scalars().first()
            
            if not literature:
                return JSONResponse(
                    content={
                        "statusCode": 404,
                        "message": "Literature not found"
                    }, status_code=status.HTTP_404_NOT_FOUND
                )

            # Bütün tərcümələri sil
            translations_query = await db.execute(
                select(LiteratureTrans)
                .where(LiteratureTrans.literature_code == literature_code)
            )
            
            translations = translations_query.scalars().all()
            
            for trans in translations:
                await db.delete(trans)

            # Literature-i sil
            await db.delete(literature)
            await db.commit()

            return JSONResponse(
                content={
                    "statusCode": 200,
                    "message": "Literature deleted successfully."
                }
            )

        except Exception as e:
            print("Delete literature error:", e)
            traceback.print_exc()
            return JSONResponse(
                content={
                    "statusCode": 500,
                    "error": str(e)
                }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    async def search_literatures(
        self,
        search_term: str,
        start: int,
        end: int,
        lang_code: str,
        specialty_code: int,
        db: AsyncSession
    ):
        """Literature-ləri ad və ya URL-ə görə axtarır"""
        try:
            # Base query conditions
            base_conditions = []
            
            if specialty_code:
                base_conditions.append(Literature.specialty_code == specialty_code)

            # Axtarış şərtləri
            if search_term:
                # URL-də axtarış
                url_condition = Literature.url.ilike(f"%{search_term}%")
                
                # Ad-da axtarış üçün translation-larla join
                name_query = select(LiteratureTrans.literature_code).where(
                    and_(
                        LiteratureTrans.language_code == lang_code,
                        LiteratureTrans.literature_name.ilike(f"%{search_term}%")
                    )
                )
                name_result = await db.execute(name_query)
                literature_codes_with_matching_names = [row[0] for row in name_result.fetchall()]
                
                # Search conditions
                search_conditions = [url_condition]
                if literature_codes_with_matching_names:
                    name_condition = Literature.literature_code.in_(literature_codes_with_matching_names)
                    search_conditions.append(name_condition)
                
                base_conditions.append(or_(*search_conditions))

            # Final condition
            if base_conditions:
                final_condition = and_(*base_conditions)
            else:
                final_condition = True

            # Total sayını hesabla
            total_query = await db.execute(
                select(func.count()).select_from(Literature).where(final_condition)
            )
            total = total_query.scalar()

            if total == 0:
                return JSONResponse(
                    content={
                        "statusCode": 204,
                        "message": "No content"
                    }, status_code=status.HTTP_200_OK
                )

            # Literature-ləri gətir
            literature_query = await db.execute(
                select(Literature)
                .where(final_condition)
                .offset(start)
                .limit(end - start)
            )

            literatures = literature_query.scalars().all()
            literature_arr = []

            for literature in literatures:
                # Tərcümələri gətir
                literature_translations_query = await db.execute(
                    select(LiteratureTrans)
                    .where(
                        and_(
                            LiteratureTrans.literature_code == literature.literature_code,
                            LiteratureTrans.language_code == lang_code
                        )
                    )
                )

                literature_translations = literature_translations_query.scalar_one_or_none()

                literature_obj = {
                    "id": literature.id,
                    "literature_code": literature.literature_code,
                    "specialty_code": literature.specialty_code,
                    "literature_name": literature_translations.literature_name if literature_translations else None,
                    "url": literature.url,
                    "created_at": literature.created_at.isoformat() if literature.created_at else None,
                    "updated_at": literature.updated_at.isoformat() if literature.updated_at else None
                }

                literature_arr.append(literature_obj)
            
            return JSONResponse(
                content={
                    "statusCode": 200,
                    "literatures": literature_arr,
                    "total": total,
                    "search_term": search_term
                }
            )
        
        except Exception as e:
            print("Search literatures error:", e)
            traceback.print_exc()
            return JSONResponse(
                content={
                    "statusCode": 500,
                    "error": str(e)
                }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )