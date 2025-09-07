# pet_report.py
# VERSION 1.2.0 - Modified to call the actual PDF generator from pdf_generator_pet.py
import logging
import os # Added for chart_image_path placeholder
logger = logging.getLogger(__name__)

# Import the actual PDF generation function from pdf_generator_pet.py
# This assumes pdf_generator_pet.py is in the same directory (package) as pet_report.py
try:
    from .pdf_generator_pet import generate_astrology_pdf as actual_generate_pet_pdf
except ImportError:
    logger.critical("Failed to import generate_astrology_pdf from .pdf_generator_pet. Ensure it's in the same package.")
    # Fallback to prevent complete crash during import, though PDF generation will fail.
    def actual_generate_pet_pdf(*args, **kwargs):
        logger.error("actual_generate_pet_pdf is not available due to import error.")
        return False

print("--- DEBUG: Importing pet_report.py (Now linking to actual PDF generator) ---")

def generate_pet_pdf(
    output_path, client_name, species,
    sections_data, occasion_style_key,
    chart_data, breed,
    # These are passed from run_pet_report.py but managed differently now or need to be added
    assets_base_dir=None, # Not a direct param of actual_generate_pet_pdf
    fonts_base_dir=None,  # Not a direct param of actual_generate_pet_pdf
    data_jsons_dir=None,  # Not a direct param of actual_generate_pet_pdf
    pet_quotes_list=None, # Not a direct param of actual_generate_pet_pdf
    # NEW required arguments for actual_generate_pet_pdf:
    chart_image_path=None,
    PET_PROMPTS=None,
    SECTION_LAYOUT_PRESETS=None,
    **kwargs # Catch any other arguments
):
    print(f"--- DEBUG: generate_pet_pdf in pet_report.py (linking to actual generator) CALLED for {client_name}! ---")
    logger.info(f"Attempting to generate PDF for {client_name} using actual PDF generation logic.")

    # --- Argument Mapping & Preparation ---
    # `sections` is `sections_data`
    # `occasion_mode` is `occasion_style_key`
    # `pet_breed` is `breed`
    # `pet_species` is `species`

    # Handle potentially missing new arguments:
    if chart_image_path is None:
        # Create a dummy placeholder path if not provided, or log an error
        # For now, let's assume pdf_generator_pet.py's smoke test logic for image creation handles this
        # if it receives None, or we make it mandatory from run_pet_report.py
        logger.warning("chart_image_path not provided to generate_pet_pdf. PDF generation might fail or use a default.")
        # Example: Use a known placeholder if you have one, or let the called function handle it.
        # This path should ideally be made robust, perhaps using assets_base_dir if that was intended for such things.
        # For now, we pass it as None and rely on pdf_generator_pet to handle it (its smoke test creates one).

    if PET_PROMPTS is None:
        logger.error("PET_PROMPTS (definitions for report sections) not provided. PDF generation will likely fail.")
        return False # Cannot generate without prompts

    if SECTION_LAYOUT_PRESETS is None:
        logger.info("SECTION_LAYOUT_PRESETS not provided, defaulting to an empty dictionary.")
        SECTION_LAYOUT_PRESETS = {}

    # The arguments like assets_base_dir, fonts_base_dir, data_jsons_dir
    # are not directly passed to pdf_generator_pet.generate_astrology_pdf.
    # That function and its PetPDFBuilder class use internal path configurations,
    # often derived from human_report or fallbacks.
    # If you need to override these, PetPDFBuilder would need to be modified
    # to accept them from its 'generation_context'.

    try:
        success = actual_generate_pet_pdf(
            output_path=output_path,
            sections=sections_data,
            client_name=client_name,
            chart_data=chart_data,
            chart_image_path=chart_image_path,
            PROMPTS_TO_USE=PET_PROMPTS,
            SECTION_LAYOUT_PRESETS=SECTION_LAYOUT_PRESETS,
            occasion_mode=occasion_style_key,
            pet_breed=breed,
            pet_species=species
            # is_pet_report=True is a default in generate_astrology_pdf
        )
        if success:
            logger.info(f"Pet PDF generated successfully via actual_generate_pet_pdf for {client_name}: {output_path}")
        else:
            logger.error(f"Pet PDF generation failed via actual_generate_pet_pdf for {client_name}.")
        return success
    except Exception as e:
        logger.critical(f"Error calling actual_generate_pet_pdf from pet_report.py for {client_name}: {e}", exc_info=True)
        return False

print("--- DEBUG: Finished defining generate_pet_pdf (linking to actual) in pet_report.py ---")

# End of modified pet_report.py 