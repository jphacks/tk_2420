from app import app
from env import OVERLAY_URL_PREFIX, VIDEO_URL_PREFIX
from models import MemberProfile, VideoInfo, db


def seed_data():
    """Initialize the database with default video data."""
    videos = [  # noqa: F841
        VideoInfo(
            id="1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p",
            title="Supernova",
            group_name="aespa",
            video_url=f"{VIDEO_URL_PREFIX}/file/Supernova.mp4",
            overlay_url=f"{OVERLAY_URL_PREFIX}/file/Supernova_overlay.json",
            original_video_width=640,
            original_video_height=360,
        ),
        VideoInfo(
            id="1q2w3e4r-5t6y-7u8i-9o0p-1a2s3d4f5g6h",
            title="Whiplash",
            group_name="aespa",
            video_url=f"{VIDEO_URL_PREFIX}/file/Whiplash.mp4",
            overlay_url=f"{OVERLAY_URL_PREFIX}/file/Whiplash_overlay.json",
            original_video_width=640,
            original_video_height=360,
        ),
        VideoInfo(
            id="7g8h9i0j-1k2l-3m4n-5o6p-1q2w3e4r5t6y",
            title="takarazuka_song",
            group_name="takarazuka",
            video_url=f"{VIDEO_URL_PREFIX}/file/Whiplash.mp4",
            overlay_url=f"{OVERLAY_URL_PREFIX}/file/Whiplash_overlay.json",
            original_video_width=640,
            original_video_height=360,
        ),
    ]

    member_profiles = [
        MemberProfile(group_member_id=0, name="giselle", associated_color="pink", group_name="aespa"),
        MemberProfile(group_member_id=1, name="karina", associated_color="blue", group_name="aespa"),
        MemberProfile(group_member_id=2, name="ningning", associated_color="purple", group_name="aespa"),
        MemberProfile(group_member_id=3, name="winter", associated_color="lightgreen", group_name="aespa"),
        MemberProfile(group_member_id=0, name="hoshikaze_madoka", associated_color="red", group_name="takarazuka"),
        MemberProfile(group_member_id=1, name="hosizora_misaki", associated_color="blue", group_name="takarazuka"),
        MemberProfile(group_member_id=2, name="minami_maito", associated_color="pink", group_name="takarazuka"),
        MemberProfile(group_member_id=3, name="oto_kurisu", associated_color="green", group_name="takarazuka"),
        MemberProfile(group_member_id=4, name="seino_asuka", associated_color="yellow", group_name="takarazuka"),
        MemberProfile(group_member_id=5, name="towaki_sea", associated_color="purple", group_name="takarazuka"),
        MemberProfile(group_member_id=6, name="yuzuka_rei", associated_color="black", group_name="takarazuka"),
        MemberProfile(group_member_id=0, name="iroha", associated_color="blue", group_name="illit"),
        MemberProfile(group_member_id=1, name="minju", associated_color="pink", group_name="illit"),
        MemberProfile(group_member_id=2, name="moka", associated_color="purple", group_name="illit"),
        MemberProfile(group_member_id=3, name="wonhee", associated_color="lightgreen", group_name="illit"),
        MemberProfile(group_member_id=4, name="yunah", associated_color="red", group_name="illit"),
    ]

    # データベースをクリアしてからデータを挿入
    with app.app_context():
        db.drop_all()
        db.create_all()
        # db.session.bulk_save_objects(videos)
        db.session.bulk_save_objects(member_profiles)
        db.session.commit()
        print("Database seeded successfully.")


if __name__ == "__main__":
    seed_data()
