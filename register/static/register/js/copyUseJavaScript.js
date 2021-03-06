    function onClickCopy() {
// コピー対象のpタグオブジェクトを取得する.
    // console.log("click");
    // let pTag = document.getElementById('copyTarget');
    // console.log("selected");
    // let range = document.createRange();
    // range.selectNodeContents(pTag);
    // let selection = window.getSelection();
    // selection.removeAllRanges();
    // selection.addRange(range);
    // // 選択したものをコピーする.
    // document.execCommand('copy');
    // // コピー内容の選択を解除する.
    // selection.removeAllRanges();
    // console.log("copied");
    let pTag = document.getElementById('copyTarget');
    pTag.select();
    document.execCommand('copy');
}
